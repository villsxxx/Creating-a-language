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
mov eax, 10
mov [rbp-4], eax
mov eax, 20
mov [rbp-8], eax
mov eax, [rbp-8]
push rax
mov eax, [rbp-4]
pop rbx
add eax, ebx
mov [rbp-12], eax
sub rsp, 32
lea rcx, [rel fmt_s]
lea rdx, [rel str_0]
call printf
add rsp, 32
mov eax, [rbp-12]
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
