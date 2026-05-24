grammar PascalSubset;

program
    : PROGRAM IDENT SEMI declarations functions block DOT EOF
    ;

functions
    : functionDecl*
    ;

functionDecl
    : FUNCTION IDENT COLON typeSpec SEMI block SEMI
    ;

declarations
    : (VAR varDeclLine)+
    | /* empty */
    ;

varDeclLine
    : identList COLON typeSpec SEMI
    ;

identList
    : IDENT (COMMA IDENT)*
    ;

typeSpec
    : INTEGER
    | CHAR
    | BOOLEAN
    | REAL
    | STRING
    | ARRAY LBRACK expression DOTDOT expression RBRACK OF typeSpec
    ;

block
    : BEGIN statementList END
    ;

statementList
    : statement (SEMI statement)*
    | /* empty */
    ;

statement
    : block
    | ifStatement
    | whileStatement
    | forStatement
    | repeatStatement
    | writeStatement
    | readStatement
    | assignmentOrCall
    ;

ifStatement
    : IF expression THEN statement (ELSE statement)?
    ;

whileStatement
    : WHILE expression DO statement
    ;

forStatement
    : FOR IDENT ASSIGN expression (TO | DOWNTO) expression DO statement
    ;

repeatStatement
    : REPEAT statementList UNTIL expression
    ;

writeStatement
    : (WRITE | WRITELN) LPAREN argumentList RPAREN
    ;

readStatement
    : (READ | READLN) LPAREN identArgList RPAREN
    ;

identArgList
    : variableRef (COMMA variableRef)*
    | /* empty */
    ;

assignmentOrCall
    : IDENT ASSIGN expression
    | IDENT LBRACK expression RBRACK ASSIGN expression
    | IDENT LPAREN argumentList RPAREN
    ;

argumentList
    : expression (COMMA expression)*
    | /* empty */
    ;

expression
    : logicalOr
    ;

logicalOr
    : logicalAnd (OR logicalAnd)*
    ;

logicalAnd
    : equality (AND equality)*
    ;

equality
    : relational ((EQ | NEQ) relational)*
    ;

relational
    : additive ((LT | GT | LE | GE) additive)*
    ;

additive
    : multiplicative ((PLUS | MINUS) multiplicative)*
    ;

multiplicative
    : unary ((MUL | DIV_FLOAT | DIV_INT | MOD) unary)*
    ;

unary
    : (MINUS | NOT) unary
    | factor
    ;

factor
    : NUMBER
    | STRING_LITERAL
    | variableRef
    | IDENT LPAREN argumentList RPAREN
    | LPAREN expression RPAREN
    ;

variableRef
    : IDENT
    | IDENT LBRACK expression RBRACK
    ;

PROGRAM : 'program';
VAR : 'var';
BEGIN : 'begin';
END : 'end';
IF : 'if';
THEN : 'then';
ELSE : 'else';
WHILE : 'while';
FOR : 'for';
TO : 'to';
DOWNTO : 'downto';
DO : 'do';
REPEAT : 'repeat';
UNTIL : 'until';
WRITE : 'write';
WRITELN : 'writeln';
READ : 'read';
READLN : 'readln';
INTEGER : 'integer';
CHAR : 'char';
BOOLEAN : 'boolean';
REAL : 'real';
STRING : 'string';
ARRAY : 'array';
OF : 'of';
AND : 'and';
OR : 'or';
NOT : 'not';
DIV_INT : 'div';
MOD : 'mod';

ASSIGN : ':=';
DOTDOT : '..';
LE : '<=';
GE : '>=';
NEQ : '<>';
EQ : '=';
LT : '<';
GT : '>';
PLUS : '+';
MINUS : '-';
MUL : '*';
DIV_FLOAT : '/';
DOT : '.';
COMMA : ',';
COLON : ':';
SEMI : ';';
LPAREN : '(';
RPAREN : ')';
LBRACK : '[';
RBRACK : ']';

NUMBER : [0-9]+ ('.' [0-9]+)?;
STRING_LITERAL : '\'' (~['\r\n])* '\'';
IDENT : [a-zA-Z_][a-zA-Z0-9_]*;

COMMENT : '{' .*? '}' -> skip;
WS : [ \t\r\n]+ -> skip;
