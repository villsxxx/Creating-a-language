from ast import (
    ArrayAccess,
    ArrayType,
    Assign,
    BinOp,
    Block,
    Cast,
    For,
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


class PythonCodeGenerator:
    def __init__(self, symbols):
        self.symbols = symbols
        self.lines = []
        self.indent = 0

    def generate(self, program_node):
        if not isinstance(program_node, Program):
            raise ValueError("Ожидается Program")

        self.lines = []
        self.indent = 0

        self._emit("def main():")
        self.indent += 1
        self._emit("# declarations")
        for decl in program_node.declarations:
            self._emit_declaration(decl)

        self._emit("")
        self._emit("# statements")
        self._emit_statement(program_node.statements)
        self.indent -= 1

        self._emit("")
        self._emit("if __name__ == '__main__':")
        self.indent += 1
        self._emit("main()")
        self.indent -= 1

        return "\n".join(self.lines) + "\n"

    def _emit(self, line):
        self.lines.append("    " * self.indent + line)

    def _emit_declaration(self, decl):
        for name in decl.names:
            var_type = decl.type
            if isinstance(var_type, SimpleType):
                self._emit(f"{name} = {self._default_value(var_type.name)}")
            elif isinstance(var_type, ArrayType):
                size = var_type.high - var_type.low + 1
                default_item = self._default_value(var_type.element_type.name)
                self._emit(f"{name} = [{default_item}] * {size}")
            else:
                raise ValueError(f"Неизвестный тип объявления: {type(var_type).__name__}")

    def _default_value(self, type_name):
        if type_name == "integer":
            return "0"
        if type_name == "real":
            return "0.0"
        if type_name == "boolean":
            return "False"
        if type_name == "string":
            return "''"
        if type_name == "char":
            return "'\\0'"
        return "None"

    def _emit_statement(self, stmt):
        if isinstance(stmt, Block):
            for s in stmt.statements:
                self._emit_statement(s)
            return

        if isinstance(stmt, Assign):
            left_code = self._expr(stmt.left)
            right_code = self._expr(stmt.right)
            self._emit(f"{left_code} = {right_code}")
            return

        if isinstance(stmt, If):
            self._emit(f"if {self._expr(stmt.condition)}:")
            self.indent += 1
            self._emit_statement(stmt.then_stmt)
            self.indent -= 1
            if stmt.else_stmt is not None:
                self._emit("else:")
                self.indent += 1
                self._emit_statement(stmt.else_stmt)
                self.indent -= 1
            return

        if isinstance(stmt, While):
            self._emit(f"while {self._expr(stmt.condition)}:")
            self.indent += 1
            self._emit_statement(stmt.body)
            self.indent -= 1
            return

        if isinstance(stmt, For):
            var_name = stmt.var.name
            start_expr = self._expr(stmt.start)
            end_expr = self._expr(stmt.end)
            if stmt.direction == "to":
                self._emit(f"for {var_name} in range({start_expr}, {end_expr} + 1):")
            else:
                self._emit(f"for {var_name} in range({start_expr}, {end_expr} - 1, -1):")
            self.indent += 1
            self._emit_statement(stmt.body)
            self.indent -= 1
            return

        if isinstance(stmt, Write):
            args_code = [f"str({self._expr(arg)})" for arg in stmt.args]
            end_value = "'\\n'" if stmt.newline else "''"
            if args_code:
                self._emit(f"print({', '.join(args_code)}, sep='', end={end_value})")
            else:
                self._emit(f"print(end={end_value})")
            return

        if isinstance(stmt, Read):
            if not stmt.args:
                self._emit("input()")
                return

            for arg in stmt.args:
                target = self._expr(arg)
                var_type = self._expression_type(arg)
                cast_fn = self._python_cast(var_type)
                self._emit(f"{target} = {cast_fn}(input())")
            return

        raise ValueError(f"Неизвестный оператор: {type(stmt).__name__}")

    def _expr(self, node):
        if isinstance(node, Literal):
            if node.type == "string":
                return repr(node.value)
            if node.type == "boolean":
                return "True" if node.value else "False"
            return repr(node.value)

        if isinstance(node, Variable):
            return node.name

        if isinstance(node, ArrayAccess):
            array_type = self.symbols[node.name]
            offset = array_type.low
            return f"{node.name}[{self._expr(node.index)} - {offset}]"

        if isinstance(node, Cast):
            return f"{self._python_cast(node.target_type)}({self._expr(node.expr)})"

        if isinstance(node, UnaryOp):
            if node.op == "not":
                return f"(not {self._expr(node.expr)})"
            return f"({node.op}{self._expr(node.expr)})"

        if isinstance(node, BinOp):
            op_map = {"=": "==", "<>": "!=", "and": "and", "or": "or", "div": "//", "mod": "%"}
            py_op = op_map.get(node.op, node.op)
            return f"({self._expr(node.left)} {py_op} {self._expr(node.right)})"

        raise ValueError(f"Неизвестное выражение: {type(node).__name__}")

    def _python_cast(self, type_name):
        return {
            "integer": "int",
            "real": "float",
            "string": "str",
            "boolean": "bool",
            "char": "str",
        }.get(type_name, "str")

    def _expression_type(self, expr):
        if isinstance(expr, Variable):
            typ = self.symbols[expr.name]
            if isinstance(typ, SimpleType):
                return typ.name
            return "string"
        if isinstance(expr, ArrayAccess):
            typ = self.symbols[expr.name]
            return typ.element_type.name
        return "string"
