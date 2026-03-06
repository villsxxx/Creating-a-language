class MathExpressionParser:
    def __init__(self, expression: str):
        self.expression = expression
        self.pos = 0

    @property
    def current(self) -> str:
        if self.pos < len(self.expression):
            return self.expression[self.pos]
        else:
            return '$'

    def NUMBER(self) -> float:
        temp = ''
        while self.current.isdigit() or self.current == '.':
            temp += self.current
            self.pos += 1
        return float(temp)

    def group(self) -> float:
        if self.current == '(':
            self.pos += 1
            res = self.add()
            self.pos += 1
        else:
            res = self.NUMBER()
        return res

    def add(self) -> float:
        res = self.mult()
        while self.current in ('+' , '-'):
            op = self.current
            self.pos += 1
            temp = self.mult()
            if op == '+':
                res = res + temp
            else:
                res = res - temp
        return res

    def mult(self) -> float:
        res = self.group()
        while self.current in ('*', '/'):
            op = self.current
            self.pos += 1
            temp = self.group()
            if op == '*':
                res = res * temp
            else:
                res = res / temp
        return res

    def result(self):
        res = self.add()
        if self.pos != len(self.expression):
            raise Exception(f'лишний символ {self.current} в позиции {self.pos}')
        return res

def main():
    expression = '3+2'
    parser = MathExpressionParser(expression)
    res = parser.result()
    print(res)

if __name__ == '__main__':
    main()