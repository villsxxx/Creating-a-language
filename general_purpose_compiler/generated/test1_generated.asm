bits 32
default rel
section .data
str_0 db "Hello, world!", 0
fmt_int db "%d", 0

section .text
extern printf
global main
main:
push ebp
mov ebp, esp
sub esp, 4
push dword str_0
call printf
add esp, 4
push 10
push dword fmt_int
call printf
add esp, 8
mov esp, ebp
pop ebp
xor eax, eax
ret
