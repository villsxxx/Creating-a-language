import sys
from parser import Parser
from error import CompilerError
from ast_printer import print_ast

def main():
    test_files = [
        "examples/test1.txt",
        "examples/test2.txt",
        "examples/test3.txt",
        "examples/test4.txt"
    ]

    for i, filename in enumerate(test_files):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
            parser = Parser(code)
            ast = parser.parse_program()
            print(f"=== {filename} ===")
            print_ast(ast)
        except CompilerError as e:
            print(f"=== {filename} ===")
            print(e.full_message())
        except FileNotFoundError:
            print(f"=== {filename} ===")
            print(f"Файл не найден: {filename}")
        if i < len(test_files) - 1:
            print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    main()
