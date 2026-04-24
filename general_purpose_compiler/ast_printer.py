from ast import *

def print_ast(node, indent=0):
    prefix = "  " * indent
    if isinstance(node, Program):
        print(f"{prefix}Program(name={node.name})")

        for decl in node.declarations:
            print_ast(decl, indent+1)
        print_ast(node.statements, indent+1)

    elif isinstance(node, VarDecl):
        print(f"{prefix}VarDecl(names={node.names}, type={node.type})")

    elif isinstance(node, Assign):
        print(f"{prefix}Assign")
        print_ast(node.left, indent+1)
        print_ast(node.right, indent+1)

    elif isinstance(node, If):
        print(f"{prefix}If")
        print_ast(node.condition, indent+1)
        print_ast(node.then_stmt, indent+1)

        if node.else_stmt:
            print_ast(node.else_stmt, indent+1)

    elif isinstance(node, While):
        print(f"{prefix}While")
        print_ast(node.condition, indent+1)
        print_ast(node.body, indent+1)

    elif isinstance(node, For):
        print(f"{prefix}For(direction={node.direction})")
        print_ast(node.var, indent+1)
        print_ast(node.start, indent+1)
        print_ast(node.end, indent+1)
        print_ast(node.body, indent+1)

    elif isinstance(node, Write):
        print(f"{prefix}Write(newline={node.newline})")
        for arg in node.args:
            print_ast(arg, indent+1)

    elif isinstance(node, Read):
        print(f"{prefix}Read(newline={node.newline})")
        for arg in node.args:
            print_ast(arg, indent+1)

    elif isinstance(node, Block):
        print(f"{prefix}Block")
        for stmt in node.statements:
            print_ast(stmt, indent+1)

    elif isinstance(node, BinOp):
        print(f"{prefix}BinOp({node.op})")
        print_ast(node.left, indent+1)
        print_ast(node.right, indent+1)

    elif isinstance(node, UnaryOp):
        print(f"{prefix}UnaryOp({node.op})")
        print_ast(node.expr, indent+1)

    elif isinstance(node, Literal):
        print(f"{prefix}Literal({node.value}, type={node.type})")

    elif isinstance(node, Variable):
        print(f"{prefix}Variable({node.name})")

    elif isinstance(node, ArrayAccess):
        print(f"{prefix}ArrayAccess({node.name})")
        print_ast(node.index, indent+1)

    elif isinstance(node, FuncCall):
        print(f"{prefix}FuncCall({node.name})")
        for arg in node.args:
            print_ast(arg, indent+1)

    elif isinstance(node, ProcCall):
        print(f"{prefix}ProcCall({node.name})")
        for arg in node.args:
            print_ast(arg, indent+1)
    else:
        print(f"{prefix}Unknown node: {node}")