from ast import *
from error import CompilerError


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, symbol):
        if name in self.symbols:
            raise CompilerError(f"Переменная '{name}' уже объявлена")
        self.symbols[name] = symbol

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None


class Symbol:
    def __init__(self, name, typ, kind='variable'):
        self.name = name
        self.type = typ
        self.kind = kind


class SemanticAnalyzer:
    def __init__(self):
        self.current_scope = None
        self.errors = []

    def analyze(self, node):
        self.current_scope = SymbolTable()
        return self.visit(node)

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        if isinstance(node, list):
            return [self.visit(item) for item in node]
        return node

    def visit_Program(self, node):
        for decl in node.declarations:
            self.visit(decl)
        self.visit(node.statements)
        return node

    def visit_VarDecl(self, node):
        for name in node.names:
            self.current_scope.define(name, Symbol(name, node.type))
        return node

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)
        return node

    def visit_Assign(self, node):
        left_type = self.get_type(node.left)
        right_type = self.get_type(node.right)

        if not self.type_compatible(left_type, right_type):
            raise CompilerError(f"Несовместимые типы: {left_type} и {right_type}")

        node.left_type = left_type
        node.right_type = right_type
        return node

    def visit_If(self, node):
        cond_type = self.get_type(node.condition)
        if cond_type != 'boolean':
            raise CompilerError(f"Ожидается boolean, найдено {cond_type}")
        self.visit(node.then_stmt)
        if node.else_stmt:
            self.visit(node.else_stmt)
        return node

    def visit_While(self, node):
        cond_type = self.get_type(node.condition)
        if cond_type != 'boolean':
            raise CompilerError(f"Ожидается boolean, найдено {cond_type}")
        self.visit(node.body)
        return node

    def visit_For(self, node):
        start_type = self.get_type(node.start)
        end_type = self.get_type(node.end)
        if start_type not in ['integer', 'char']:
            raise CompilerError(f"Цикл for требует integer или char, найдено {start_type}")
        if end_type not in ['integer', 'char']:
            raise CompilerError(f"Цикл for требует integer или char, найдено {end_type}")
        self.visit(node.body)
        return node

    def visit_Write(self, node):
        for arg in node.args:
            self.get_type(arg)
        return node

    def visit_Read(self, node):
        for arg in node.args:
            if isinstance(arg, Variable):
                sym = self.current_scope.lookup(arg.name)
                if not sym:
                    raise CompilerError(f"Переменная '{arg.name}' не объявлена")
            elif isinstance(arg, ArrayAccess):
                sym = self.current_scope.lookup(arg.name)
                if not sym:
                    raise CompilerError(f"Массив '{arg.name}' не объявлен")
        return node

    def visit_BinOp(self, node):
        left_type = self.get_type(node.left)
        right_type = self.get_type(node.right)

        if node.op in ['+', '-', '*', '/']:
            if left_type not in ['integer', 'real'] or right_type not in ['integer', 'real']:
                raise CompilerError(f"Операция {node.op} требует числовых типов")
            node.type = 'real' if 'real' in [left_type, right_type] else 'integer'
        elif node.op in ['div', 'mod']:
            if left_type != 'integer' or right_type != 'integer':
                raise CompilerError(f"Операция {node.op} требует integer")
            node.type = 'integer'
        elif node.op in ['=', '<>', '<', '>', '<=', '>=']:
            if not self.type_compatible(left_type, right_type):
                raise CompilerError(f"Несовместимые типы для сравнения")
            node.type = 'boolean'
        elif node.op in ['and', 'or']:
            if left_type != 'boolean' or right_type != 'boolean':
                raise CompilerError(f"Логическая операция требует boolean")
            node.type = 'boolean'
        else:
            node.type = left_type
        return node

    def visit_UnaryOp(self, node):
        expr_type = self.get_type(node.expr)
        if node.op == 'not':
            if expr_type != 'boolean':
                raise CompilerError(f"Операция not требует boolean")
            node.type = 'boolean'
        elif node.op == '-':
            if expr_type not in ['integer', 'real']:
                raise CompilerError(f"Унарный минус требует числового типа")
            node.type = expr_type
        return node

    def visit_Variable(self, node):
        sym = self.current_scope.lookup(node.name)
        if not sym:
            raise CompilerError(f"Переменная '{node.name}' не объявлена")
        node.type = sym.type
        return node

    def visit_ArrayAccess(self, node):
        sym = self.current_scope.lookup(node.name)
        if not sym:
            raise CompilerError(f"Массив '{node.name}' не объявлен")
        if not sym.type.startswith('array'):
            raise CompilerError(f"'{node.name}' не является массивом")

        index_type = self.get_type(node.index)
        if index_type != 'integer':
            raise CompilerError(f"Индекс массива должен быть integer")

        node.type = self.extract_array_element_type(sym.type)
        return node

    def visit_Literal(self, node):
        return node

    def visit_FuncCall(self, node):
        func_types = {
            'Inc': ['integer'], 'Dec': ['integer'], 'Abs': ['integer', 'real'],
            'Length': ['string'], 'Pos': ['string', 'string'], 'Copy': ['string', 'integer', 'integer']
        }
        if node.name in func_types:
            expected = func_types[node.name]
            if len(node.args) != len(expected):
                raise CompilerError(f"Функция {node.name} ожидает {len(expected)} аргументов")
        return node

    def visit_ProcCall(self, node):
        return node

    def get_type(self, node):
        if hasattr(node, 'type'):
            return node.type
        elif isinstance(node, Literal):
            return node.type
        elif isinstance(node, Variable):
            sym = self.current_scope.lookup(node.name)
            return sym.type if sym else None
        elif isinstance(node, ArrayAccess):  # 🔥 ДОБАВЛЕНО: обработка доступа к массиву
            self.visit(node)
            return node.type
        elif isinstance(node, BinOp):
            self.visit(node)
            return node.type
        elif isinstance(node, UnaryOp):
            self.visit(node)
            return node.type
        return None

    def type_compatible(self, t1, t2):
        if t1 == t2: return True
        if 'integer' in [t1, t2] and 'real' in [t1, t2]: return True
        return False

    def extract_array_element_type(self, array_type):
        if array_type.startswith('array['):
            parts = array_type.split(' of ')
            if len(parts) == 2:
                return parts[1]
        return None