from ast import (
    ArrayAccess,
    Assign,
    BinOp,
    Block,
    For,
    FunctionDecl,
    If,
    Literal,
    Program,
    UnaryOp,
    Variable,
    While,
)


def optimize(program):
    if not isinstance(program, Program):
        return program
    for fn in program.functions:
        fn.body = _opt_block(fn.body)
    program.statements = _opt_block(program.statements)
    return program


def _opt_block(block):
    if not isinstance(block, Block):
        return block
    new_stmts = []
    for stmt in block.statements:
        new_stmts.append(_opt_stmt(stmt))
    return Block(new_stmts)


def _opt_stmt(stmt):
    if isinstance(stmt, Block):
        return _opt_block(stmt)
    if isinstance(stmt, Assign):
        return Assign(stmt.left, _opt_expr(stmt.right))
    if isinstance(stmt, If):
        cond = _opt_expr(stmt.condition)
        if isinstance(cond, Literal) and cond.type == "boolean":
            if cond.value:
                return _opt_stmt(stmt.then_stmt)
            if stmt.else_stmt is not None:
                return _opt_stmt(stmt.else_stmt)
            return Block([])
        return If(cond, _opt_stmt(stmt.then_stmt), _opt_stmt(stmt.else_stmt) if stmt.else_stmt else None)
    if isinstance(stmt, While):
        return While(_opt_expr(stmt.condition), _opt_stmt(stmt.body))
    if isinstance(stmt, For):
        return For(stmt.var, _opt_expr(stmt.start), _opt_expr(stmt.end), _opt_stmt(stmt.body), stmt.direction)
    return stmt


def _opt_expr(node):
    if isinstance(node, BinOp):
        left = _opt_expr(node.left)
        right = _opt_expr(node.right)
        folded = _fold_binop(node.op, left, right)
        if folded is not None:
            return folded
        if node.op == "+" and _is_zero(right):
            return left
        if node.op == "+" and _is_zero(left):
            return right
        if node.op == "-" and _is_zero(right):
            return left
        if node.op == "*" and _is_one(right):
            return left
        if node.op == "*" and _is_one(left):
            return right
        if node.op == "*" and (_is_zero(left) or _is_zero(right)):
            return Literal(0, "integer")
        return BinOp(left, node.op, right)
    if isinstance(node, UnaryOp):
        expr = _opt_expr(node.expr)
        if node.op == "-" and isinstance(expr, Literal) and expr.type in ("integer", "real"):
            return Literal(-expr.value, expr.type)
        if node.op == "not" and isinstance(expr, Literal) and expr.type == "boolean":
            return Literal(not expr.value, "boolean")
        return UnaryOp(node.op, expr)
    if isinstance(node, ArrayAccess):
        return ArrayAccess(node.name, _opt_expr(node.index))
    return node


def _is_zero(node):
    return isinstance(node, Literal) and node.type in ("integer", "real") and node.value == 0


def _is_one(node):
    return isinstance(node, Literal) and node.type == "integer" and node.value == 1


def _fold_binop(op, left, right):
    if not isinstance(left, Literal) or not isinstance(right, Literal):
        return None
    if left.type != right.type:
        return None
    if left.type not in ("integer", "real", "boolean"):
        return None
    if op in ("+", "-", "*", "/", "div", "mod"):
        if left.type != "integer" and op in ("div", "mod"):
            return None
        a, b = left.value, right.value
        if op == "+":
            v = a + b
        elif op == "-":
            v = a - b
        elif op == "*":
            v = a * b
        elif op == "/":
            v = a / b
        elif op == "div":
            v = a // b
        else:
            v = a % b
        return Literal(v, left.type)
    if op in ("=", "<>", "<", ">", "<=", ">="):
        ops = {"=": lambda x, y: x == y, "<>": lambda x, y: x != y, "<": lambda x, y: x < y,
               ">": lambda x, y: x > y, "<=": lambda x, y: x <= y, ">=": lambda x, y: x >= y}
        return Literal(ops[op](left.value, right.value), "boolean")
    if op in ("and", "or"):
        if left.type != "boolean":
            return None
        v = left.value and right.value if op == "and" else left.value or right.value
        return Literal(v, "boolean")
    return None
