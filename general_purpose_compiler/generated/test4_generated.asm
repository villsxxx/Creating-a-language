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
mov eax, 1
mov [ebp-4], eax
.while_1:
mov eax, 5
push eax
mov eax, [ebp-4]
pop ebx
cmp eax, ebx
mov eax, 0
setg al
movzx eax, al
xor eax, 1
cmp eax, 0
je .endwhile_2
mov eax, [ebp-4]
push eax
push dword fmt_int
call printf
add esp, 8
push 10
push dword fmt_int
call printf
add esp, 8
mov eax, 1
push eax
mov eax, [ebp-4]
pop ebx
add eax, ebx
mov [ebp-4], eax
jmp .while_1
.endwhile_2:
mov esp, ebp
pop ebp
xor eax, eax
ret
