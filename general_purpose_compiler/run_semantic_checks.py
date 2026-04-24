from pathlib import Path

from error import CompilerError
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def run_file(path):
    code = path.read_text(encoding="utf-8")
    parser = Parser(code)
    ast = parser.parse_program()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)


def main():
    examples_dir = Path("examples/semantic_errors")
    files = sorted(examples_dir.glob("*.txt"))

    if not files:
        print("Нет файлов в examples/semantic_errors")
        return

    for i, file_path in enumerate(files):
        print(f"===== {file_path.name} =====")
        try:
            run_file(file_path)
            print("Семантических ошибок нет (для этого файла это неожиданно).")
        except CompilerError as error:
            print(error.full_message())

        if i < len(files) - 1:
            print()


if __name__ == "__main__":
    main()
