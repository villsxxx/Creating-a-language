import sys
from pathlib import Path
from parser import Parser
from error import CompilerError
from ast_printer import print_ast
from semantic_analyzer import SemanticAnalyzer
from code_generator import PythonCodeGenerator

def main():
    test_files = [
        "examples/test1.txt",
        "examples/test2.txt",
        "examples/test3.txt",
        "examples/test4.txt",
        "examples/test5.txt",
    ]

    output_dir = Path("generated")
    output_dir.mkdir(exist_ok=True)

    for i, filename in enumerate(test_files):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()

            parser = Parser(code)
            ast = parser.parse_program()
            analyzer = SemanticAnalyzer()
            ast = analyzer.analyze(ast)

            generator = PythonCodeGenerator(analyzer.symbols)
            generated_code = generator.generate(ast)
            generated_file = output_dir / (Path(filename).stem + "_generated.py")
            generated_file.write_text(generated_code, encoding="utf-8")

            print(f"{'*'*5} {filename}{'*'*5}")
            print_ast(ast)
            print(f"Сгенерирован исполняемый файл: {generated_file}")
        except CompilerError as e:
            print(f"{'*'*5} {filename} {'*'*5}")
            print(e.full_message())
        except FileNotFoundError:
            print(f"{'*'*5} {filename} {'*'*5}")
            print(f"Файл не найден: {filename}")
        if i < len(test_files) - 1:
            print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    main()
