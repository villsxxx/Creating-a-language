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
    ProcCall,
    Program,
    Read,
    SimpleType,
    UnaryOp,
    VarDecl,
    Variable,
    While,
    Write,
)
from error import CompilerError


class SemanticAnalyzer:
    """
    Простая семантическая проверка:
    - объявления и использование переменных;
    - проверки типов;
    - вставка Cast в AST (типозависимая модификация).
    """

    def __init__(self):
        self.symbols = {}

    def analyze(self, program_node):
        if not isinstance(program_node, Program):
            raise CompilerError("Ожидается узел Program для семантического анализа")

        self._collect_declarations(program_node.declarations)
        self._visit_block(program_node.statements)
        return program_node

    def _collect_declarations(self, declarations):
        for decl in declarations:
            if not isinstance(decl, VarDecl):
                continue
            normalized_type = self._normalize_type(decl.type)
            decl.type = normalized_type

            for name in decl.names:
                if name in self.symbols:
                    raise CompilerError(f"Повторное объявление переменной '{name}'")
                self.symbols[name] = normalized_type

    def _normalize_type(self, type_node):
        if isinstance(type_node, SimpleType):
            return type_node

        if isinstance(type_node, ArrayType):
            low = self._require_int_constant(type_node.low, "Нижняя граница массива")
            high = self._require_int_constant(type_node.high, "Верхняя граница массива")
            if high < low:
                raise CompilerError("Верхняя граница массива меньше нижней")
            element_type = self._normalize_type(type_node.element_type)
            return ArrayType(low, high, element_type)

        raise CompilerError("Неизвестный тип в объявлении")

    def _require_int_constant(self, node, error_prefix):
        if not isinstance(node, Literal) or node.type != "integer":
            raise CompilerError(f"{error_prefix} должна быть целочисленной константой")
        return node.value

    def _visit_block(self, block):
        if not isinstance(block, Block):
            raise CompilerError("Ожидается блок операторов")
        for stmt in block.statements:
            self._visit_statement(stmt)

    def _visit_statement(self, stmt):
        if isinstance(stmt, Block):
            self._visit_block(stmt)
            return

        if isinstance(stmt, Assign):
            self._check_assign(stmt)
            return

        if isinstance(stmt, If):
            cond_type = self._expr_type(stmt.condition)
            if cond_type != "boolean":
                raise CompilerError("Условие if должно иметь тип boolean")
            self._visit_statement(stmt.then_stmt)
            if stmt.else_stmt is not None:
                self._visit_statement(stmt.else_stmt)
            return

        if isinstance(stmt, While):
            cond_type = self._expr_type(stmt.condition)
            if cond_type != "boolean":
                raise CompilerError("Условие while должно иметь тип boolean")
            self._visit_statement(stmt.body)
            return

        if isinstance(stmt, For):
            var_type = self._expr_type(stmt.var)
            if var_type != "integer":
                raise CompilerError("Счетчик for должен иметь тип integer")
            start_type = self._expr_type(stmt.start)
            end_type = self._expr_type(stmt.end)
            if start_type != "integer" or end_type != "integer":
                raise CompilerError("Границы for должны иметь тип integer")
            self._visit_statement(stmt.body)
            return

        if isinstance(stmt, Write):
            for i, arg in enumerate(stmt.args):
                self._expr_type(arg)
                stmt.args[i] = arg
            return

        if isinstance(stmt, Read):
            for arg in stmt.args:
                arg_type = self._expr_type(arg)
                if arg_type.startswith("array"):
                    raise CompilerError("Нельзя читать значение прямо в массив")
            return

        if isinstance(stmt, ProcCall):
            for arg in stmt.args:
                self._expr_type(arg)
            return

        raise CompilerError(f"Неизвестный оператор: {type(stmt).__name__}")

    def _check_assign(self, stmt):
        left_type = self._expr_type(stmt.left)
        right_type = self._expr_type(stmt.right)

        if left_type == right_type:
            return

        if left_type == "real" and right_type == "integer":
            stmt.right = Cast(stmt.right, "real")
            return

        raise CompilerError(
            f"Несовместимые типы в присваивании: слева {left_type}, справа {right_type}"
        )

    def _expr_type(self, node):
        if isinstance(node, Literal):
            return node.type

        if isinstance(node, Cast):
            self._expr_type(node.expr)
            return node.target_type

        if isinstance(node, Variable):
            if node.name not in self.symbols:
                raise CompilerError(f"Использована необъявленная переменная '{node.name}'")
            typ = self.symbols[node.name]
            if isinstance(typ, ArrayType):
                return self._array_signature(typ)
            return typ.name

        if isinstance(node, ArrayAccess):
            if node.name not in self.symbols:
                raise CompilerError(f"Использована необъявленная переменная '{node.name}'")
            var_type = self.symbols[node.name]
            if not isinstance(var_type, ArrayType):
                raise CompilerError(f"Переменная '{node.name}' не является массивом")
            index_type = self._expr_type(node.index)
            if index_type != "integer":
                raise CompilerError("Индекс массива должен иметь тип integer")
            if isinstance(node.index, Literal):
                if node.index.value < var_type.low or node.index.value > var_type.high:
                    raise CompilerError(
                        f"Индекс {node.index.value} выходит за границы массива [{var_type.low}..{var_type.high}]"
                    )
            if isinstance(var_type.element_type, SimpleType):
                return var_type.element_type.name
            return self._array_signature(var_type.element_type)

        if isinstance(node, UnaryOp):
            expr_type = self._expr_type(node.expr)
            if node.op == "-":
                if expr_type not in ("integer", "real"):
                    raise CompilerError("Унарный минус применим только к integer/real")
                return expr_type
            if node.op == "not":
                if expr_type != "boolean":
                    raise CompilerError("Оператор not применим только к boolean")
                return "boolean"
            raise CompilerError(f"Неизвестный унарный оператор '{node.op}'")

        if isinstance(node, BinOp):
            left_type = self._expr_type(node.left)
            right_type = self._expr_type(node.right)
            op = node.op

            if op in ("+", "-", "*", "/", "div", "mod"):
                return self._numeric_binop_type(node, left_type, right_type, op)

            if op in ("=", "<>", "<", ">", "<=", ">="):
                if left_type != right_type:
                    if {"integer", "real"} == {left_type, right_type}:
                        self._promote_to_real(node, left_type, right_type)
                    else:
                        raise CompilerError(
                            f"Нельзя сравнивать {left_type} и {right_type}"
                        )
                return "boolean"

            if op in ("and", "or"):
                if left_type != "boolean" or right_type != "boolean":
                    raise CompilerError(f"Оператор {op} требует boolean-операнды")
                return "boolean"

            raise CompilerError(f"Неизвестный бинарный оператор '{op}'")

        raise CompilerError(f"Неизвестное выражение: {type(node).__name__}")

    def _numeric_binop_type(self, node, left_type, right_type, op):
        if op in ("div", "mod"):
            if left_type != "integer" or right_type != "integer":
                raise CompilerError(f"Оператор {op} работает только с integer")
            return "integer"

        if left_type not in ("integer", "real") or right_type not in ("integer", "real"):
            raise CompilerError(f"Оператор {op} работает только с integer/real")

        if op == "/":
            self._promote_to_real(node, left_type, right_type)
            return "real"

        if left_type == right_type:
            return left_type

        self._promote_to_real(node, left_type, right_type)
        return "real"

    def _promote_to_real(self, node, left_type, right_type):
        if left_type == "integer" and right_type == "real":
            node.left = Cast(node.left, "real")
        elif left_type == "real" and right_type == "integer":
            node.right = Cast(node.right, "real")

    def _array_signature(self, array_type):
        return f"array[{array_type.low}..{array_type.high}]"
