from typing import Union
from contextlib import suppress

class ParsingError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Parser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    @property
    def current(self) -> str:
        if self.pos < len(self.text):
            return self.text[self.pos]
        else:
            return '$'

    def ws(self):
        while self.current.isspace():
            self.pos += 1

    def parse(self, s1: str, *s: str) -> Union[str, None]:
        self.ws()
        for ss in (s1, *s):
            if self.text[self.pos:self.pos + len(ss)] == ss:
                self.pos += len(ss)
                self.ws()
                return ss
        raise ParsingError(f'Ни один фрагмент из {s1, *s} не найден!')

    def is_parse(self, s1: str, *s: str) -> Union[str, None]:
        pos = self.pos
        res = None
        with suppress(ParsingError):
            res = self.parse(s1, *s)
        if res is None:
            self.pos = pos
        return res