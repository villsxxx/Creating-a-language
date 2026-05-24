bits 32
default rel
section .data
str_0 db "Sum = ", 0
fmt_int db "%d", 0

section .text
extern printf
global main
main:
push ebp
mov ebp, esp
sub esp, 16
mov eax, 10
mov [ebp-4], eax
mov eax, 20
mov [ebp-8], eax
mov eax, [ebp-8]
push eax
mov eax, [ebp-4]
pop ebx
add eax, ebx
mov [ebp-12], eax
push dword str_0
call printf
add esp, 4
mov eax, [ebp-12]
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
