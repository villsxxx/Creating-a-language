import sys
from parser import Parser
from error import CompilerError
from ast_printer import print_ast

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
        print_ast(ast)
    except CompilerError as e:
        print(e.full_message())
        sys.exit(1)

if __name__ == '__main__':
    main()

