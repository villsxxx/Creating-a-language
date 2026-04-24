import re
from error import CompilerError

class Token:
    def __init__(self, kind, value, line, column):
        self.kind = kind
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.kind}, {self.value}, {self.line}:{self.column})"

class Lexer:
    spec = [
        ('NUMBER', r'\d+(\.\d+)?'),
        ('STRING', r"'([^']*)'"),
        ('IDENT', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('KEYWORD',
         r'program|var|begin|end|if|then|else|while|for|to|downto|do|repeat|until|write|writeln|read|readln|integer|char|boolean|real|string|array|of|and|or|not|div|mod'),
        ('OP', r':=|[<>]=|<>|[<>]|[+\-*/=]'),
        ('DOTDOT', r'\.\.'),
        ('DOT', r'\.'),
        ('COMMA', r','),
        ('COLON', r':'),
        ('SEMICOLON', r';'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('WHITESPACE', r'\s+'),
        ('COMMENT', r'\{[^}]*\}'),
    ]
    master_re = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in spec))

    def __init__(self, code):
        self.code = code
        self.tokens = []

    def tokenize(self):
        pos = 0
        line = 1
        line_start = 0

        while pos < len(self.code):
            match = self.master_re.match(self.code, pos)
            if not match:
                bad_char = self.code[pos]
                col = pos - line_start + 1
                raise CompilerError(f'Недопустимый символ {bad_char!r}', line, col)

            kind = match.lastgroup
            value = match.group()

            if kind == 'WHITESPACE':
                if '\n' in value:
                    line += value.count('\n')
                    line_start = match.end()
            elif kind == 'COMMENT':
                if '\n' in value:
                    line += value.count('\n')
                    line_start = match.end()
            else:
                col = match.start() - line_start + 1
                if kind == 'IDENT' and value in self.get_keywords():
                    kind = 'KEYWORD'
                self.tokens.append(Token(kind, value, line, col))

            pos = match.end()

        return self.tokens

    def get_keywords(self):
        return {'program', 'var', 'begin', 'end', 'if', 'then', 'else', 'while',
                'for', 'to', 'downto', 'do', 'repeat', 'until', 'write', 'writeln',
                'read', 'readln', 'integer', 'char', 'boolean', 'real', 'string',
                'array', 'of', 'and', 'or', 'not', 'div', 'mod'}