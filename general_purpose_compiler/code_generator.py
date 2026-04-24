from ast import *
import re


class CodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.code = []
        self.temp_counter = 0

    def generate(self, node):
        self.visit(node)
        return '\n'.join(self.code)

    def visit(self, node, *args, **kwargs):
        method_name = 'visit_' + type(node).__name__
        method = getattr(self, method_name, self.generic_visit)
        return method(node, *args, **kwargs)

    def generic_visit(self, node):
        if isinstance(node, list):
            for item in node:
                self.visit(item)

    def indent(self):
        return '    ' * self.indent_level

    def visit_Program(self, node):
        self.code.append("# Generated from Pascal program")
        self.code.append("")

        for decl in node.declarations:
            self.visit(decl)

        self.code.append("")
        self.code.append("def main():")
        self.indent_level += 1
        self.visit(node.statements)
        self.indent_level -= 1

        self.code.append("")
        self.code.append("if __name__ == '__main__':")
        self.code.append("    main()")

    def visit_VarDecl(self, node):
        for name in node.names:
            if node.type == 'integer':
                self.code.append(f"{name} = 0")
            elif node.type == 'real':
                self.code.append(f"{name} = 0.0")
            elif node.type == 'boolean':
                self.code.append(f"{name} = False")
            elif node.type == 'char':
                self.code.append(f"{name} = ''")
            elif node.type == 'string':
                self.code.append(f"{name} = ''")
            elif node.type.startswith('array['):
                self.generate_array_decl(name, node.type)

    def generate_array_decl(self, name, array_type):
        match = re.match(r'array\[(\d+)\.\.(\d+)\]\s+of\s+(\w+)', array_type)
        if match:
            low, high, elem_type = match.groups()
            low, high = int(low), int(high)
            size = high - low + 1

            if elem_type == 'integer':
                init = '0'
            elif elem_type == 'real':
                init = '0.0'
            elif elem_type == 'boolean':
                init = 'False'
            else:
                init = "''"

            self.code.append(f"{name} = [{init} for _ in range({size})]")
            self.code.append(f"def {name}_idx(i):")
            self.code.append(f"    return {name}[i - ({low})]")
            self.code.append(f"def {name}_set(i, val):")
            self.code.append(f"    {name}[i - ({low})] = val")

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Assign(self, node):
        right_code = self.generate_expression(node.right)

        if isinstance(node.left, ArrayAccess):
            idx_code = self.generate_expression(node.left.index)
            self.code.append(f"{self.indent()}{node.left.name}_set({idx_code}, {right_code})")
        else:
            left_code = self.generate_expression(node.left)
            self.code.append(f"{self.indent()}{left_code} = {right_code}")

    def visit_If(self, node):
        cond = self.generate_expression(node.condition)
        self.code.append(f"{self.indent()}if {cond}:")
        self.indent_level += 1
        self.visit(node.then_stmt)
        self.indent_level -= 1

        if node.else_stmt:
            self.code.append(f"{self.indent()}else:")
            self.indent_level += 1
            self.visit(node.else_stmt)
            self.indent_level -= 1

    def visit_While(self, node):
        cond = self.generate_expression(node.condition)
        self.code.append(f"{self.indent()}while {cond}:")
        self.indent_level += 1
        self.visit(node.body)
        self.indent_level -= 1

    def visit_For(self, node):
        var = self.generate_expression(node.var)
        start = self.generate_expression(node.start)
        end = self.generate_expression(node.end)

        if node.direction == 'to':
            self.code.append(f"{self.indent()}for {var} in range({start}, {end} + 1):")
        else:
            self.code.append(f"{self.indent()}for {var} in range({start}, {end} - 1, -1):")

        self.indent_level += 1
        self.visit(node.body)
        self.indent_level -= 1

    def visit_Write(self, node):
        args = [self.generate_expression(arg) for arg in node.args]
        if node.newline:
            self.code.append(f"{self.indent()}print({', '.join(args)})")
        else:
            self.code.append(f"{self.indent()}print({', '.join(args)}, end='')")

    def visit_Read(self, node):
        for arg in node.args:
            var_name = self.generate_expression(arg)
            self.code.append(f"{self.indent()}{var_name} = input()")

    def visit_BinOp(self, node, *args):
        left = self.generate_expression(node.left)
        right = self.generate_expression(node.right)

        op_map = {
            '+': '+', '-': '-', '*': '*', '/': '/',
            'div': '//', 'mod': '%',
            '=': '==', '<>': '!=',
            '<': '<', '>': '>', '<=': '<=', '>=': '>=',
            'and': 'and', 'or': 'or'
        }

        op = op_map.get(node.op, node.op)
        return f"({left} {op} {right})"

    def visit_UnaryOp(self, node, *args):
        expr = self.generate_expression(node.expr)

        if node.op == 'not':
            return f"(not {expr})"
        elif node.op == '-':
            return f"(-{expr})"

        return expr

    def visit_Variable(self, node, *args):
        return node.name

    def visit_ArrayAccess(self, node, *args):
        name = node.name
        idx = self.generate_expression(node.index)
        return f"{name}_idx({idx})"

    def visit_Literal(self, node, *args):
        if node.type == 'string':
            return f"'{node.value}'"
        elif node.type == 'boolean':
            return 'True' if node.value else 'False'
        else:
            return str(node.value)

    def visit_FuncCall(self, node, *args):
        args_code = [self.generate_expression(arg) for arg in node.args]

        func_map = {
            'Inc': lambda a: f"{a[0]} += 1",
            'Dec': lambda a: f"{a[0]} -= 1",
            'Abs': lambda a: f"abs({a[0]})",
            'Length': lambda a: f"len({a[0]})",
            'Pos': lambda a: f"{a[0]}.find({a[1]}) + 1",
            'Copy': lambda a: f"{a[0]}[{a[1]}-1:{a[1]}-1+{a[2]}]"
        }

        if node.name in func_map:
            return func_map[node.name](args_code)

        return f"{node.name}({', '.join(args_code)})"

    def visit_ProcCall(self, node, *args):
        args_code = [self.generate_expression(arg) for arg in node.args]
        self.code.append(f"{self.indent()}{node.name}({', '.join(args_code)})")

    def generate_expression(self, node):
        if isinstance(node, (Literal, Variable, ArrayAccess)):
            return self.visit(node)
        elif isinstance(node, (BinOp, UnaryOp)):
            return self.visit(node)
        elif isinstance(node, FuncCall):
            return self.visit(node)
        else:
            return str(node)