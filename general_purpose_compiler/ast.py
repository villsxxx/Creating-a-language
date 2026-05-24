class ASTNode:
    pass


class TypeSpec(ASTNode):
    pass


class SimpleType(TypeSpec):
    def __init__(self, name):
        self.name = name


class ArrayType(TypeSpec):
    def __init__(self, low, high, element_type):
        self.low = low
        self.high = high
        self.element_type = element_type


class Program(ASTNode):
    def __init__(self, name, declarations, statements, functions=None):
        self.name = name
        self.declarations = declarations
        self.functions = functions or []
        self.statements = statements

class FunctionDecl(ASTNode):
    def __init__(self, name, result_type, body):
        self.name = name
        self.result_type = result_type
        self.body = body

class VarDecl(ASTNode):
    def __init__(self, names, typ):
        self.names = names
        self.type = typ

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

class ArrayAccess(ASTNode):
    def __init__(self, name, index):
        self.name = name
        self.index = index

class Literal(ASTNode):
    def __init__(self, value, typ):
        self.value = value
        self.type = typ

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


class Cast(ASTNode):
    def __init__(self, expr, target_type):
        self.expr = expr
        self.target_type = target_type

class FuncCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Assign(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class If(ASTNode):
    def __init__(self, condition, then_stmt, else_stmt=None):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class For(ASTNode):
    def __init__(self, var, start, end, body, direction='to'):
        self.var = var
        self.start = start
        self.end = end
        self.body = body
        self.direction = direction

class Write(ASTNode):
    def __init__(self, args, newline=False):
        self.args = args
        self.newline = newline

class Read(ASTNode):
    def __init__(self, args, newline=False):
        self.args = args
        self.newline = newline

class ProcCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements