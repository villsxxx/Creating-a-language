from pathlib import Path
from parser import Parser
from error import CompilerError
from ast_printer import print_ast
from semantic_analyzer import SemanticAnalyzer
from optimizer import optimize
from code_generator import PythonCodeGenerator
from x86_codegen import X86CodeGenerator
from interpreter import Interpreter

def compile_file(filename, output_dir):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    parser = Parser(code)
    ast = parser.parse_program()
    analyzer = SemanticAnalyzer()
    ast = analyzer.analyze(ast)
    ast = optimize(ast)

    stem = Path(filename).stem
    py_gen = PythonCodeGenerator(analyzer.symbols, ast.functions)
    py_path = output_dir / (stem + "_generated.py")
    py_path.write_text(py_gen.generate(ast), encoding="utf-8")

    x86_gen = X86CodeGenerator(analyzer.symbols, ast.functions)
    asm_path = output_dir / (stem + "_generated.asm")
    asm_path.write_text(x86_gen.generate(ast), encoding="utf-8")

    interp = Interpreter(analyzer.symbols, ast.functions)
    if stem == "test3":
        interp.set_inputs(["10"])
    output = interp.run(ast)

    return ast, py_path, asm_path, output

def main():
    test_files = [
        "examples/test1.txt",
        "examples/test2.txt",
        "examples/test3.txt",
        "examples/test4.txt",
        "examples/test5.txt",
        "examples/test6_function.txt",
    ]

    output_dir = Path("generated")
    output_dir.mkdir(exist_ok=True)

    for i, filename in enumerate(test_files):
        try:
            ast, py_path, asm_path, interp_out = compile_file(filename, output_dir)

            print(f"{'*'*5} {filename}{'*'*5}")
            print_ast(ast)
            print(f"Python: {py_path}")
            print(f"x86: {asm_path}")
            if interp_out:
                print("Интерпретатор:", "".join(interp_out), end="")
            else:
                print("Интерпретатор: (нет вывода)")
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
