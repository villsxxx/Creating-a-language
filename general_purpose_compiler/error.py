
class CompilerError(Exception):
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.full_message())

    def full_message(self):
        if self.line is not None and self.column is not None:
            return f"Ошибка в {self.line}:{self.column}: {self.message}"
        else:
            return f"Ошибка: {self.message}"
