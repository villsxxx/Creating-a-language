bits 64
default rel
section .data
str_0 db "Sum = ", 0
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
mov [rbp-24], eax
.while_1:
mov eax, 5
push rax
mov eax, [rbp-24]
pop rbx
cmp eax, ebx
mov eax, 0
setle al
movzx eax, al
cmp eax, 0
je .endwhile_2
mov eax, 2
push rax
mov eax, [rbp-24]
pop rbx
imul eax, ebx
mov ecx, eax
mov eax, [rbp-24]
sub eax, 1
movsxd rax, eax
imul rax, rax, 4
mov rdx, rbp
sub rdx, 4
sub rdx, rax
mov [rdx], ecx
mov eax, 1
push rax
mov eax, [rbp-24]
pop rbx
add eax, ebx
mov [rbp-24], eax
jmp .while_1
.endwhile_2:
mov eax, 0
mov [rbp-28], eax
mov eax, 1
mov [rbp-24], eax
.forcheck_3:
mov eax, 5
mov ebx, eax
mov eax, [rbp-24]
cmp eax, ebx
jg .forend_4
mov eax, [rbp-24]
sub eax, 1
movsxd rax, eax
imul rax, rax, 4
mov rdx, rbp
sub rdx, 4
sub rdx, rax
mov eax, dword [rdx]
push rax
mov eax, [rbp-28]
pop rbx
add eax, ebx
mov [rbp-28], eax
mov eax, [rbp-24]
inc eax
mov [rbp-24], eax
jmp .forcheck_3
.forend_4:
sub rsp, 32
lea rcx, [rel fmt_s]
lea rdx, [rel str_0]
call printf
add rsp, 32
mov eax, [rbp-28]
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
mov rsp, rbp
pop rbp
xor eax, eax
ret
