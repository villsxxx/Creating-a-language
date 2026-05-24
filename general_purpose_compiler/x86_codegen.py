from ast import (
    ArrayAccess,
    ArrayType,
    Assign,
    BinOp,
    Block,
    For,
    FunctionDecl,
    If,
    Literal,
    Program,
    Read,
    SimpleType,
    UnaryOp,
    Variable,
    While,
    Write,
)


class X86CodeGenerator:
    def __init__(self, symbols, functions):
        self.symbols = symbols
        self.functions = {fn.name: fn for fn in functions}
        self.lines = []
        self.data = []
        self.var_offset = {}
        self.stack_size = 0
        self.label_id = 0
        self.string_labels = {}

    def generate(self, program):
        if not isinstance(program, Program):
            raise ValueError("Ожидается Program")
        self.lines = []
        self.data = []
        self.string_labels = {}
        self.var_offset = {}
        self._reserve_vars(program.declarations)
        self._scan_strings(program.statements)
        for fn in program.functions:
            self._scan_strings(fn.body)
        self._emit("bits 64")
        self._emit("default rel")
        self._emit("section .data")
        for line in self.data:
            self._emit(line)
        self._emit("fmt_int db \"%d\", 0")
        self._emit("fmt_s db \"%s\", 0")
        self._emit("fmt_in db \"%d\", 0")
        self._emit("fmt_char db \"%c\", 10, 0")
        self._emit("")
        self._emit("section .text")
        self._emit("extern printf")
        self._emit("extern scanf")
        for fn in program.functions:
            self._emit_function(fn)
        self._emit("global main")
        self._emit("main:")
        self._emit("push rbp")
        self._emit("mov rbp, rsp")
        self._emit("and rsp, -16")
        if self.stack_size > 0:
            self._emit(f"sub rsp, {self.stack_size}")
        self._emit_statement(program.statements)
        self._emit("mov rsp, rbp")
        self._emit("pop rbp")
        self._emit("xor eax, eax")
        self._emit("ret")
        return "\n".join(self.lines) + "\n"

    def _emit(self, line):
        self.lines.append(line)

    def _reserve_vars(self, declarations):
        offset = 4
        for decl in declarations:
            for name in decl.names:
                self.var_offset[name] = offset
                if isinstance(decl.type, ArrayType):
                    offset += (decl.type.high - decl.type.low + 1) * 4
                else:
                    offset += 4
        self.stack_size = max(48, ((offset + 15) // 16) * 16)

    def _next_label(self, prefix):
        self.label_id += 1
        return f".{prefix}_{self.label_id}"

    def _emit_function(self, fn):
        label = f"fn_{fn.name}"
        self._emit(f"{label}:")
        self._emit("push rbp")
        self._emit("mov rbp, rsp")
        self._emit("and rsp, -16")
        self._emit("sub rsp, 16")
        self._emit_statement(fn.body)
        self._emit("mov eax, [rbp-4]")
        self._emit("mov rsp, rbp")
        self._emit("pop rbp")
        self._emit("ret")

    def _emit_statement(self, stmt):
        if isinstance(stmt, Block):
            for s in stmt.statements:
                self._emit_statement(s)
            return
        if isinstance(stmt, Assign):
            self._push_expr(stmt.right)
            if isinstance(stmt.left, Variable):
                if stmt.left.name in self.functions:
                    self._emit("mov [rbp-4], eax")
                else:
                    off = self.var_offset[stmt.left.name]
                    self._emit(f"mov [rbp-{off}], eax")
            elif isinstance(stmt.left, ArrayAccess):
                self._emit("mov ecx, eax")
                self._array_store(stmt.left, "ecx")
            return
        if isinstance(stmt, If):
            else_label = self._next_label("else")
            end_label = self._next_label("endif")
            self._push_expr(stmt.condition)
            self._emit("cmp eax, 0")
            self._emit(f"je {else_label}")
            self._emit_statement(stmt.then_stmt)
            if stmt.else_stmt is not None:
                self._emit(f"jmp {end_label}")
                self._emit(f"{else_label}:")
                self._emit_statement(stmt.else_stmt)
                self._emit(f"{end_label}:")
            else:
                self._emit(f"{else_label}:")
            return
        if isinstance(stmt, While):
            start = self._next_label("while")
            end = self._next_label("endwhile")
            self._emit(f"{start}:")
            self._push_expr(stmt.condition)
            self._emit("cmp eax, 0")
            self._emit(f"je {end}")
            self._emit_statement(stmt.body)
            self._emit(f"jmp {start}")
            self._emit(f"{end}:")
            return
        if isinstance(stmt, For):
            off = self.var_offset[stmt.var.name]
            self._push_expr(stmt.start)
            self._emit(f"mov [rbp-{off}], eax")
            check = self._next_label("forcheck")
            end_lbl = self._next_label("forend")
            self._emit(f"{check}:")
            self._push_expr(stmt.end)
            self._emit("mov ebx, eax")
            self._emit(f"mov eax, [rbp-{off}]")
            self._emit("cmp eax, ebx")
            if stmt.direction == "to":
                self._emit(f"jg {end_lbl}")
            else:
                self._emit(f"jl {end_lbl}")
            self._emit_statement(stmt.body)
            self._emit(f"mov eax, [rbp-{off}]")
            if stmt.direction == "to":
                self._emit("inc eax")
            else:
                self._emit("dec eax")
            self._emit(f"mov [rbp-{off}], eax")
            self._emit(f"jmp {check}")
            self._emit(f"{end_lbl}:")
            return
        if isinstance(stmt, Read):
            for arg in stmt.args:
                if isinstance(arg, Variable):
                    off = self.var_offset[arg.name]
                    self._emit("sub rsp, 32")
                    self._emit("lea rcx, [rel fmt_in]")
                    self._emit(f"lea rdx, [rbp-{off}]")
                    self._emit("call scanf")
                    self._emit("add rsp, 32")
            return
        if isinstance(stmt, Write):
            for arg in stmt.args:
                if isinstance(arg, Literal) and arg.type == "string":
                    label = self._string_label(arg.value)
                    self._emit_printf_string(label)
                else:
                    self._push_expr(arg)
                    self._emit_printf_int()
            if stmt.newline:
                self._emit("mov edx, 10")
                self._emit("sub rsp, 32")
                self._emit("lea rcx, [rel fmt_char]")
                self._emit("call printf")
                self._emit("add rsp, 32")
            return

    def _array_index_in_rax(self, access):
        arr = self.symbols[access.name]
        self._push_expr(access.index)
        self._emit(f"sub eax, {arr.low}")
        self._emit("movsxd rax, eax")

    def _array_store(self, access, value_reg):
        base = self.var_offset[access.name]
        self._array_index_in_rax(access)
        self._emit("imul rax, rax, 4")
        self._emit("mov rdx, rbp")
        self._emit(f"sub rdx, {base}")
        self._emit("sub rdx, rax")
        self._emit(f"mov [rdx], {value_reg}")

    def _array_load(self, access):
        base = self.var_offset[access.name]
        self._array_index_in_rax(access)
        self._emit("imul rax, rax, 4")
        self._emit("mov rdx, rbp")
        self._emit(f"sub rdx, {base}")
        self._emit("sub rdx, rax")
        self._emit("mov eax, dword [rdx]")

    def _emit_printf_string(self, label):
        self._emit("sub rsp, 32")
        self._emit("lea rcx, [rel fmt_s]")
        self._emit(f"lea rdx, [rel {label}]")
        self._emit("call printf")
        self._emit("add rsp, 32")

    def _emit_printf_int(self, prep=True):
        if prep:
            self._emit("mov edx, eax")
        self._emit("sub rsp, 32")
        self._emit("lea rcx, [rel fmt_int]")
        self._emit("call printf")
        self._emit("add rsp, 32")

    def _scan_strings(self, node):
        if isinstance(node, Write):
            for arg in node.args:
                if isinstance(arg, Literal) and arg.type == "string":
                    self._string_label(arg.value)
            return
        if isinstance(node, Block):
            for stmt in node.statements:
                self._scan_strings(stmt)
            return
        if isinstance(node, If):
            self._scan_strings(node.then_stmt)
            if node.else_stmt:
                self._scan_strings(node.else_stmt)
            return
        if isinstance(node, (While, For)):
            self._scan_strings(node.body)
            return

    def _string_label(self, text):
        if text not in self.string_labels:
            label = f"str_{len(self.string_labels)}"
            self.string_labels[text] = label
            escaped = text.replace("\\", "\\\\").replace('"', '\\"')
            self.data.append(f'{label} db "{escaped}", 0')
        return self.string_labels[text]

    def _push_expr(self, node):
        if isinstance(node, Literal):
            if node.type == "boolean":
                self._emit(f"mov eax, {1 if node.value else 0}")
            elif node.type != "string":
                self._emit(f"mov eax, {node.value}")
            return
        if isinstance(node, Variable):
            if node.name in self.functions:
                self._emit(f"call fn_{node.name}")
                return
            off = self.var_offset[node.name]
            self._emit(f"mov eax, [rbp-{off}]")
            return
        if isinstance(node, ArrayAccess):
            self._array_load(node)
            return
        if isinstance(node, UnaryOp):
            self._push_expr(node.expr)
            if node.op == "-":
                self._emit("neg eax")
            else:
                self._emit("xor eax, 1")
            return
        if isinstance(node, BinOp):
            self._push_expr(node.right)
            self._emit("push rax")
            self._push_expr(node.left)
            self._emit("pop rbx")
            self._emit_binop(node.op)
            return

    def _emit_binop(self, op):
        if op == "+":
            self._emit("add eax, ebx")
        elif op == "-":
            self._emit("sub eax, ebx")
        elif op == "*":
            self._emit("imul eax, ebx")
        elif op in ("div", "mod"):
            self._emit("cdq")
            self._emit("idiv ebx")
            if op == "mod":
                self._emit("mov eax, edx")
        elif op in ("=", "<>", "<", ">", "<=", ">="):
            self._emit("cmp eax, ebx")
            self._emit("mov eax, 0")
            sets = {"=": "sete", "<>": "setne", "<": "setl", ">": "setg", "<=": "setle", ">=": "setge"}
            self._emit(f"{sets[op]} al")
            self._emit("movzx eax, al")
        elif op == "and":
            self._emit("and eax, ebx")
        elif op == "or":
            self._emit("or eax, ebx")
