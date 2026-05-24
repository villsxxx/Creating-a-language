import sys
from parser import Parser
from error import CompilerError
from ast_printer import print_ast
from semantic_analyzer import SemanticAnalyzer
from optimizer import optimize
from code_generator import PythonCodeGenerator
from interpreter import Interpreter

def main():
    input_string = """
    var
        x, y: integer;
    
    begin
        readln(x);
        readln(y);
    
        writeln('x = ', x, ', y = ', y);
    
        x := y;
        y := x;
    
        writeln('x = ', x, ', y = ', y);
    end.
    """

    try:
        parser = Parser(input_string)
        ast = parser.parse_program()
        analyzer = SemanticAnalyzer()
        ast = analyzer.analyze(ast)
        ast = optimize(ast)
        generator = PythonCodeGenerator(analyzer.symbols, ast.functions)
        generated_code = generator.generate(ast)
        output = Interpreter(analyzer.symbols, ast.functions).run(ast)

        print_ast(ast)
        print("\n--- Generated Python code ---\n")
        print(generated_code)
        if output:
            print("\n--- Interpreter output ---\n")
            print("".join(output), end="")
    except CompilerError as e:
        print(e.full_message())
        sys.exit(1)

if __name__ == '__main__':
    main()

