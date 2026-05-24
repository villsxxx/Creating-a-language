bits 32
default rel
section .data
fmt_int db "%d", 0

section .text
extern printf
global main
main:
push ebp
mov ebp, esp
sub esp, 8
mov eax, 0
push eax
mov eax, [ebp-4]
pop ebx
cmp eax, ebx
mov eax, 0
setg al
movzx eax, al
cmp eax, 0
je .else_1
push dword str_0
call printf
add esp, 4
push 10
push dword fmt_int
call printf
add esp, 8
jmp .endif_2
.else_1:
push dword str_1
call printf
add esp, 4
push 10
push dword fmt_int
call printf
add esp, 8
.endif_2:
mov esp, ebp
pop ebp
xor eax, eax
ret
