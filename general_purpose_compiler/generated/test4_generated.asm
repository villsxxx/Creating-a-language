bits 64
default rel
section .data
fmt_int db "%d", 0
fmt_s db "%s", 0
fmt_in db "%d", 0
fmt_char db "%c", 10, 0

section .text
extern printf
extern scanf
global main
main:
push rbp
mov rbp, rsp
and rsp, -16
sub rsp, 48
mov eax, 1
mov [rbp-4], eax
.while_1:
mov eax, 5
push rax
mov eax, [rbp-4]
pop rbx
cmp eax, ebx
mov eax, 0
setg al
movzx eax, al
xor eax, 1
cmp eax, 0
je .endwhile_2
mov eax, [rbp-4]
mov edx, eax
sub rsp, 32
lea rcx, [rel fmt_int]
call printf
add rsp, 32
mov edx, 10
sub rsp, 32
lea rcx, [rel fmt_char]
call printf
add rsp, 32
mov eax, 1
push rax
mov eax, [rbp-4]
pop rbx
add eax, ebx
mov [rbp-4], eax
jmp .while_1
.endwhile_2:
mov rsp, rbp
pop rbp
xor eax, eax
ret
