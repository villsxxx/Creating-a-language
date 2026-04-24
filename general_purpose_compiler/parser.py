from lexer import Lexer, Token
from error import CompilerError
from ast import *

class Parser:
    def __init__(self, code):
        self.lexer = Lexer(code)
        self.tokens = self.lexer.tokenize()
        self.pos = 0
        self.current = self.tokens[0] if self.tokens else None

    def consume(self):
        tok = self.current
        self.pos += 1
        self.current = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        return tok

    def check(self, kind=None, value=None):
        if not self.current:
            return False
        if kind and self.current.kind != kind:
            return False
        if value and self.current.value != value:
            return False
        return True

    def expect(self, kind=None, value=None):
        if not self.check(kind, value):
            if self.current:
                raise CompilerError(f"Ожидается {kind or value}, найдено {self.current.value}",
                                    self.current.line, self.current.column)
            else:
                raise CompilerError(f"Ожидается {kind or value}, но достигнут конец файла")
        return True

    def parse_program(self):
        if self.check(value='program'):
            self.consume()
            if self.check(kind='IDENT'):
                name = self.consume().value
            else:
                raise CompilerError("Ожидается имя программы", self.current.line, self.current.column)
            self.expect(value=';')
            self.consume()
        else:
            name = None
        decls = self.parse_declarations()

        self.expect(value='begin')
        self.consume()

        statements = self.parse_statements()

        self.expect(value='end')
        self.consume()

        if self.check(value='.'):
            self.consume()
        else:
            raise CompilerError("Ожидается '.' в конце программы",self.current.line if self.current else 0,self.current.column if self.current else 0)

        if self.current:
            raise CompilerError("Лишний код после точки", self.current.line, self.current.column)

        return Program(name, decls, Block(statements))

    def parse_declarations(self):
        decls = []
        while self.check(value='var'):
            self.consume()
            while self.check(kind='IDENT'):
                names = []
                names.append(self.consume().value)
                while self.check(value=','):
                    self.consume()
                    if self.check(kind='IDENT'):
                        names.append(self.consume().value)

                self.expect(value=':')
                self.consume()

                typ = self.parse_type()

                self.expect(value=';')
                self.consume()

                decls.append(VarDecl(names, typ))
        return decls

    def parse_type(self):
        if self.check(value='integer') or self.check(value='char') or self.check(value='boolean') or self.check(
                value='real') or self.check(value='string'):
            return SimpleType(self.consume().value)
        elif self.check(value='array'):
            self.consume()
            self.expect(value='[')
            self.consume()
            low = self.parse_expression()
            self.expect(value='..')
            self.consume()
            high = self.parse_expression()
            self.expect(value=']')
            self.consume()
            self.expect(value='of')
            self.consume()
            elem_type = self.parse_type()
            return ArrayType(low, high, elem_type)
        else:
            raise CompilerError("Ожидается тип", self.current.line, self.current.column)

    def parse_statements(self):
        stmts = []
        while not self.check(value='end'):
            stmts.append(self.parse_statement())
            if self.check(value=';'):
                self.consume()
        return stmts

    def parse_statement(self):
        if self.check(value='begin'):
            return self.parse_block()
        elif self.check(value='if'):
            return self.parse_if()
        elif self.check(value='while'):
            return self.parse_while()
        elif self.check(value='for'):
            return self.parse_for()
        elif self.check(value='repeat'):
            return self.parse_repeat()
        elif self.check(value='write') or self.check(value='writeln'):
            return self.parse_write()
        elif self.check(value='read') or self.check(value='readln'):
            return self.parse_read()
        elif self.check(kind='IDENT'):
            return self.parse_assignment_or_call()
        else:
            raise CompilerError(f"Неожиданный токен {self.current.value}", self.current.line, self.current.column)

    def parse_block(self):
        self.consume()
        stmts = self.parse_statements()
        self.expect(value='end')
        self.consume()
        return Block(stmts)

    def parse_if(self):
        self.consume()
        condition = self.parse_expression()
        self.expect(value='then')
        self.consume()
        then_stmt = self.parse_statement()
        else_stmt = None
        if self.check(value='else'):
            self.consume()
            else_stmt = self.parse_statement()
        return If(condition, then_stmt, else_stmt)

    def parse_while(self):
        self.consume()
        condition = self.parse_expression()
        self.expect(value='do')
        self.consume()
        body = self.parse_statement()
        return While(condition, body)

    def parse_for(self):
        self.consume()
        if self.check(kind='IDENT'):
            var_name = self.consume().value
        else:
            raise CompilerError("Ожидается переменная", self.current.line, self.current.column)

        self.expect(value=':=')
        self.consume()
        start = self.parse_expression()

        if self.check(value='to') or self.check(value='downto'):
            direction = self.consume().value
        else:
            raise CompilerError("Ожидается 'to' или 'downto'", self.current.line, self.current.column)

        end = self.parse_expression()

        self.expect(value='do')
        self.consume()
        body = self.parse_statement()

        return For(Variable(var_name), start, end, body, direction)

    def parse_repeat(self):
        self.consume()
        stmts = []
        while not self.check(value='until'):
            stmts.append(self.parse_statement())
            if self.check(value=';'):
                self.consume()

        self.expect(value='until')
        self.consume()
        condition = self.parse_expression()

        return While(UnaryOp('not', condition), Block(stmts))

    def parse_write(self):
        newline = self.current.value == 'writeln'
        self.consume()

        self.expect(value='(')
        self.consume()

        args = []
        if not self.check(value=')'):
            args.append(self.parse_expression())
            while self.check(value=','):
                self.consume()
                args.append(self.parse_expression())

        self.expect(value=')')
        self.consume()

        return Write(args, newline)

    def parse_read(self):
        newline = self.current.value == 'readln'
        self.consume()

        self.expect(value='(')
        self.consume()

        args = []
        if not self.check(value=')'):
            if self.check(kind='IDENT'):
                args.append(Variable(self.consume().value))
            while self.check(value=','):
                self.consume()
                if self.check(kind='IDENT'):
                    args.append(Variable(self.consume().value))

        self.expect(value=')')
        self.consume()

        return Read(args, newline)

    def parse_assignment_or_call(self):
        name = self.consume().value

        if self.check(value=':='):
            self.consume()
            right = self.parse_expression()
            return Assign(Variable(name), right)
        elif self.check(value='['):
            self.consume()
            index = self.parse_expression()
            self.expect(value=']')
            self.consume()
            self.expect(value=':=')
            self.consume()
            right = self.parse_expression()
            return Assign(ArrayAccess(name, index), right)
        elif self.check(value='('):
            self.consume()
            args = []
            if not self.check(value=')'):
                args.append(self.parse_expression())
                while self.check(value=','):
                    self.consume()
                    args.append(self.parse_expression())
            self.expect(value=')')
            self.consume()
            return ProcCall(name, args)
        else:
            raise CompilerError(f"Ожидается ':=' или '(', найдено {self.current.value if self.current else 'EOF'}", self.current.line if self.current else 0, self.current.column if self.current else 0)

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        node = self.parse_logical_and()
        while self.check(value='or'):
            op = self.consume().value
            right = self.parse_logical_and()
            node = BinOp(node, op, right)
        return node

    def parse_logical_and(self):
        node = self.parse_equality()
        while self.check(value='and'):
            op = self.consume().value
            right = self.parse_equality()
            node = BinOp(node, op, right)
        return node

    def parse_equality(self):
        node = self.parse_relational()
        while self.check(value='=') or self.check(value='<>'):
            op = self.consume().value
            right = self.parse_relational()
            node = BinOp(node, op, right)
        return node

    def parse_relational(self):
        node = self.parse_additive()
        while self.check(value='<') or self.check(value='>') or self.check(value='<=') or self.check(value='>='):
            op = self.consume().value
            right = self.parse_additive()
            node = BinOp(node, op, right)
        return node

    def parse_additive(self):
        node = self.parse_multiplicative()
        while self.check(value='+') or self.check(value='-'):
            op = self.consume().value
            right = self.parse_multiplicative()
            node = BinOp(node, op, right)
        return node

    def parse_multiplicative(self):
        node = self.parse_unary()
        while self.check(value='*') or self.check(value='/') or self.check(value='div') or self.check(value='mod'):
            op = self.consume().value
            right = self.parse_unary()
            node = BinOp(node, op, right)
        return node

    def parse_unary(self):
        if self.check(value='-') or self.check(value='not'):
            op = self.consume().value
            expr = self.parse_unary()
            return UnaryOp(op, expr)
        return self.parse_factor()

    def parse_factor(self):
        if self.check(kind='NUMBER'):
            value = self.consume().value
            if '.' in value:
                return Literal(float(value), 'real')
            else:
                return Literal(int(value), 'integer')
        elif self.check(kind='STRING'):
            value = self.consume().value
            return Literal(value[1:-1], 'string')
        elif self.check(kind='IDENT'):
            name = self.consume().value
            if self.check(value='['):
                self.consume()
                index = self.parse_expression()
                self.expect(value=']')
                self.consume()
                return ArrayAccess(name, index)
            elif self.check(value='('):
                self.consume()
                args = []
                if not self.check(value=')'):
                    args.append(self.parse_expression())
                    while self.check(value=','):
                        self.consume()
                        args.append(self.parse_expression())
                self.expect(value=')')
                self.consume()
                return FuncCall(name, args)
            else:
                return Variable(name)
        elif self.check(value='('):
            self.consume()
            node = self.parse_expression()
            self.expect(value=')')
            self.consume()
            return node
        else:
            raise CompilerError(f"Неожиданный токен в выражении: {self.current.value}", self.current.line, self.current.column)