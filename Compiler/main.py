import math
import builtins

from parser import Parser


class MathExpressionParser(Parser):
    def __init__(self, expression):
        super().__init__(expression)
        self.vars = {}

    def NUMBER(self) -> float:
        self.ws()
        result = ''
        while self.current.isdigit() or self.current == '.':
            result += self.current
            self.pos += 1
        if not result:
            raise Exception(f'Ожидалось число в позиции {self.pos}')
        self.ws()
        return float(result)

    def IDENT(self) -> str:
        self.ws()
        result = ''
        if self.current.isalpha():
            while self.current.isalnum():
                result += self.current
                self.pos += 1
        self.ws()
        return result

    def group(self) -> float:
        if self.is_parse('('):
            result = self.expression()
            self.parse(')')
            return result
        elif self.current.isalpha():
            pos = self.pos
            ident = self.IDENT()
            if self.is_parse('('):
                self.pos = pos
                result = self.call()
            else:
                # Это переменная
                if ident not in self.vars:
                    raise Exception(f'Не найдена переменная {ident}')
                result = self.vars[ident]
            return result
        else:
            return self.NUMBER()

    def add(self) -> float:
        res = self.mult()
        while True:
            op = self.is_parse('+', '-')
            if op is None:
                break
            temp = self.mult()
            if op == '+':
                res = res + temp
            else:
                res = res - temp
        return res

    def expression(self) -> float:
        return self.add()

    def params(self) -> list[float]:
        result = []
        if not self.is_parse(')'):
            result.append(self.expression())
            while self.is_parse(','):
                result.append(self.expression())
        return result

    def mult(self) -> float:
        res = self.group()
        while True:
            op = self.is_parse('*', '/')
            if op is None:
                break
            temp = self.group()
            if op == '*':
                res = res * temp
            else:
                res = res / temp
        return res

    def result(self):
        res = self.add()
        if self.pos != len(self.text):
            raise Exception(f'Лишний символ {self.current} в позиции {self.pos}')
        return res

    def call(self):
        ident = self.IDENT()
        self.parse('(')
        params = self.params()
        self.parse(')')
        func = globals().get(ident) or getattr(math, ident, None) or getattr(builtins, ident, None)
        if not callable(func):
            raise Exception(f'Не найдена функция {ident}')
        return func(*params)

    def stmt(self):
        pos = self.pos
        ident = self.IDENT()
        if self.is_parse('('):
            self.pos = pos
            self.call()
        else:
            self.parse('=')
            val = self.expression()
            self.vars[ident] = val

    def stmts(self) -> None:
        self.ws()
        while self.pos < len(self.text) and self.current != '}':
            self.stmt()

    def program(self):
        pass

    def input(self):
        pass

def main():
    expression = '3+2*2'
    parser = MathExpressionParser(expression)
    res = parser.result()
    print(res)

if __name__ == '__main__':
    main()