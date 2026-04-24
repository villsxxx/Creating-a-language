import sys
from parser import Parser
from error import CompilerError
from ast_printer import print_ast
from semantic_analyzer import SemanticAnalyzer
from code_generator import PythonCodeGenerator

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
        generator = PythonCodeGenerator(analyzer.symbols)
        generated_code = generator.generate(ast)

        print_ast(ast)
        print("\n--- Generated Python code ---\n")
        print(generated_code)
    except CompilerError as e:
        print(e.full_message())
        sys.exit(1)

if __name__ == '__main__':
    main()

