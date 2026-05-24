bits 32
default rel
section .data
str_0 db "x = ", 0
fmt_int db "%d", 0

section .text
extern printf
fn_five:
push ebp
mov ebp, esp
sub esp, 4
mov eax, 5
mov [ebp-4], eax
mov eax, [ebp-4]
mov esp, ebp
pop ebp
ret
global main
main:
push ebp
mov ebp, esp
sub esp, 8
call fn_five
mov [ebp-4], eax
push dword str_0
call printf
add esp, 4
mov eax, [ebp-4]
push eax
push dword fmt_int
call printf
add esp, 8
push 10
push dword fmt_int
call printf
add esp, 8
mov esp, ebp
pop ebp
xor eax, eax
ret
