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
sub esp, 32
mov eax, 1
mov [ebp-24], eax
.while_1:
mov eax, 5
push eax
mov eax, [ebp-24]
pop ebx
cmp eax, ebx
mov eax, 0
setle al
movzx eax, al
cmp eax, 0
je .endwhile_2
mov eax, 2
push eax
mov eax, [ebp-24]
pop ebx
imul eax, ebx
mov ebx, eax
mov eax, [ebp-24]
sub eax, 1
mov [ebp-4+eax*4], ebx
mov eax, 1
push eax
mov eax, [ebp-24]
pop ebx
add eax, ebx
mov [ebp-24], eax
jmp .while_1
.endwhile_2:
mov eax, 0
mov [ebp-28], eax
mov eax, 1
mov [ebp-24], eax
.forcheck_3:
mov eax, [ebp-24]
push eax
mov eax, 5
pop ebx
cmp eax, ebx
jg .forend_4
mov eax, [ebp-24]
sub eax, 1
mov eax, [ebp-4+eax*4]
push eax
mov eax, [ebp-28]
pop ebx
add eax, ebx
mov [ebp-28], eax
mov eax, [ebp-24]
inc eax
mov [ebp-24], eax
jmp .forcheck_3
.forend_4:
push dword str_0
call printf
add esp, 4
mov eax, [ebp-28]
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
