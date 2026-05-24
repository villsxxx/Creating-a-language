from ast import (
    ArrayAccess,
    ArrayType,
    Assign,
    BinOp,
    Block,
    Cast,
    For,
    FuncCall,
    FunctionDecl,
    If,
    Literal,
    ProcCall,
    Program,
    Read,
    SimpleType,
    UnaryOp,
    Variable,
    While,
    Write,
)


class Interpreter:
    def __init__(self, symbols, function_nodes):
        self.symbols = symbols
        self.function_nodes = {fn.name: fn for fn in function_nodes}
        self.vars = {}
        self.output = []
        self.input_queue = []

    def set_inputs(self, values):
        self.input_queue = list(values)

    def run(self, program):
        if not isinstance(program, Program):
            raise ValueError("Ожидается Program")
        self._init_vars(program.declarations)
        self._exec_block(program.statements)
        return self.output

    def _init_vars(self, declarations):
        for decl in declarations:
            for name in decl.names:
                self.vars[name] = self._default(decl.type)

    def _default(self, typ):
        if isinstance(typ, SimpleType):
            if typ.name == "integer":
                return 0
            if typ.name == "real":
                return 0.0
            if typ.name == "boolean":
                return False
            if typ.name == "string":
                return ""
            if typ.name == "char":
                return "\0"
        if isinstance(typ, ArrayType):
            size = typ.high - typ.low + 1
            item = self._default(typ.element_type)
            return [item] * size
        return None

    def _call_function(self, name):
        fn = self.function_nodes[name]
        saved = dict(self.vars)
        self.vars[name] = self._default(fn.result_type)
        self._exec_block(fn.body)
        value = self.vars.get(name, self._default(fn.result_type))
        self.vars = saved
        return value

    def _exec_block(self, block):
        if not isinstance(block, Block):
            self._exec_stmt(block)
            return
        for stmt in block.statements:
            self._exec_stmt(stmt)

    def _exec_stmt(self, stmt):
        if isinstance(stmt, Block):
            self._exec_block(stmt)
            return
        if isinstance(stmt, Assign):
            value = self._eval(stmt.right)
            if isinstance(stmt.left, Variable):
                self.vars[stmt.left.name] = value
            elif isinstance(stmt.left, ArrayAccess):
                arr = self.vars[stmt.left.name]
                offset = self.symbols[stmt.left.name].low
                arr[self._eval(stmt.left.index) - offset] = value
            return
        if isinstance(stmt, If):
            if self._eval(stmt.condition):
                self._exec_stmt(stmt.then_stmt)
            elif stmt.else_stmt is not None:
                self._exec_stmt(stmt.else_stmt)
            return
        if isinstance(stmt, While):
            while self._eval(stmt.condition):
                self._exec_stmt(stmt.body)
            return
        if isinstance(stmt, For):
            var_name = stmt.var.name
            start = self._eval(stmt.start)
            end = self._eval(stmt.end)
            if stmt.direction == "to":
                values = range(start, end + 1)
            else:
                values = range(start, end - 1, -1)
            for v in values:
                self.vars[var_name] = v
                self._exec_stmt(stmt.body)
            return
        if isinstance(stmt, Write):
            text = ""
            for arg in stmt.args:
                text += self._format(arg)
            if stmt.newline:
                text += "\n"
            self.output.append(text)
            return
        if isinstance(stmt, Read):
            for arg in stmt.args:
                raw = self.input_queue.pop(0) if self.input_queue else input()
                target = arg.name
                typ = self.symbols[target]
                if isinstance(typ, SimpleType):
                    self.vars[target] = self._cast_input(raw, typ.name)
            return
        if isinstance(stmt, ProcCall):
            return

    def _format(self, node):
        value = self._eval(node)
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def _cast_input(self, raw, type_name):
        if type_name == "integer":
            return int(raw)
        if type_name == "real":
            return float(raw)
        if type_name == "boolean":
            return raw.strip().lower() in ("true", "1", "yes")
        return raw

    def _eval(self, node):
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, FuncCall):
            return self._call_function(node.name)
        if isinstance(node, Variable):
            if node.name in self.function_nodes:
                return self._call_function(node.name)
            return self.vars[node.name]
        if isinstance(node, ArrayAccess):
            offset = self.symbols[node.name].low
            return self.vars[node.name][self._eval(node.index) - offset]
        if isinstance(node, Cast):
            val = self._eval(node.expr)
            if node.target_type == "real":
                return float(val)
            if node.target_type == "integer":
                return int(val)
            return val
        if isinstance(node, UnaryOp):
            val = self._eval(node.expr)
            if node.op == "-":
                return -val
            return not val
        if isinstance(node, BinOp):
            left = self._eval(node.left)
            right = self._eval(node.right)
            if node.op == "+":
                return left + right
            if node.op == "-":
                return left - right
            if node.op == "*":
                return left * right
            if node.op == "/":
                return left / right
            if node.op == "div":
                return left // right
            if node.op == "mod":
                return left % right
            if node.op == "=":
                return left == right
            if node.op == "<>":
                return left != right
            if node.op == "<":
                return left < right
            if node.op == ">":
                return left > right
            if node.op == "<=":
                return left <= right
            if node.op == ">=":
                return left >= right
            if node.op == "and":
                return left and right
            if node.op == "or":
                return left or right
        raise ValueError(f"Неизвестное выражение: {type(node).__name__}")
