import math
import builtins
from parser import Parser

class MathExpressionParser(Parser):

    def NUMBER(self) -> float:
        self.ws()
        result = ''
        while self.current.isdigit() or self.current == '.':
            result += self.current
            self.pos += 1
        if not result:
            raise Exception(f'Ожидалось число в позиции {self.pos}')
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
        elif self.current.isalpha():
            ident = self.IDENT()
            self.parse('(')
            params = self.params()
            self.parse(')')

            func = globals().get(ident) or getattr(math, ident, None) or getattr(builtins, ident, None)
            if not callable(func):
                raise Exception(f'Не найдена функция {ident}')
            result = func(*params)
        else:
            result = self.NUMBER()
        return result

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

def main():
    expression = '3+2*2'
    parser = MathExpressionParser(expression)
    res = parser.result()
    print(res)

if __name__ == '__main__':
    main()