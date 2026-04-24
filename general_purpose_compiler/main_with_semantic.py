import os
import sys
import subprocess
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
from error import CompilerError
from ast_printer import print_ast


def compile_and_run(code, filename):
    print(f"\n")
    print(f"ФАЙЛ: {filename}")
    print()


    print(" Лексический анализ ")
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print(f"Успешно: найдено {len(tokens)} токенов.")
    except CompilerError as e:
        print(f"Ошибка: {e.full_message()}")
        return


    print("\n Синтаксический анализ (AST) ")
    try:
        parser = Parser(code)
        ast = parser.parse_program()
        print("AST построено успешно.")
        print_ast(ast)
    except CompilerError as e:
        print(f"Ошибка: {e.full_message()}")
        return


    print("\n Семантический анализ ")
    analyzer = SemanticAnalyzer()
    try:
        ast = analyzer.analyze(ast)
        print("Проверка типов пройдена успешно.")
    except CompilerError as e:
        print(f"Ошибка: {e.full_message()}")
        return


    print("\n Выполнение программы ")
    try:
        generator = CodeGenerator()
        python_code = generator.generate(ast)

        with open("temp_generated_script.py", "w", encoding="utf-8") as f:
            f.write(python_code)

        result = subprocess.run(
            [sys.executable, "temp_generated_script.py"],
            capture_output=True,
            text=True
        )


        if result.stdout:
            print("Вывод программы:")
            print(result.stdout)

        if result.returncode != 0:
            print(f"Ошибка выполнения (Runtime Error): {result.stderr}")

    except Exception as e:
        print(f"Критическая ошибка компилятора: {e}")


def main():

    examples_dir = "examples"

    test_files = ["test1.txt", "test2.txt", "test3.txt", "test4.txt", "test5.txt"]


    for test_file in test_files:
        file_path = os.path.join(examples_dir, test_file)

        if not os.path.exists(file_path):
            print(f"Файл {file_path} не найден. Пропускаем...")
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            compile_and_run(code, test_file)
        except Exception as e:
            print(f"Не удалось прочитать файл {test_file}: {e}")


if __name__ == '__main__':
    main()