import sys
from parser import Parser
from error import CompilerError
from ast_printer import print_ast

def main():
    input_string = """
program test;
var a, b: integer;
begin
    a := 10;
    b := a + 20;
    writeln('Result: ', b);
end.
"""
    try:
        parser = Parser(input_string)
        ast = parser.parse_program()
        print("\nAST дерево:")
        print_ast(ast)
    except CompilerError as e:
        print(e.full_message())
        sys.exit(1)

if __name__ == '__main__':
    main()

