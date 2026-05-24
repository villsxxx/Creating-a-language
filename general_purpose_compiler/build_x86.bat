@echo off
setlocal
cd /d "%~dp0"

set ASM=%~1
if "%ASM%"=="" set ASM=generated\test2_generated.asm

for %%F in ("%ASM%") do set BASE=%%~nF
set OBJ=generated\%BASE%.obj
set EXE=generated\%BASE%.exe

echo [1/3] nasm: %ASM%
nasm -f win64 "%ASM%" -o "%OBJ%"
if errorlevel 1 (
    echo NASM failed. Install NASM and reopen terminal.
    exit /b 1
)

echo [2/3] gcc: %OBJ%
if exist "%EXE%" del /f /q "%EXE%" 2>nul
gcc -no-pie "%OBJ%" -o "%EXE%"
if errorlevel 1 (
    set EXE_NEW=generated\%BASE%_new.exe
    echo Retrying as %EXE_NEW% ...
    gcc -no-pie "%OBJ%" -o "%EXE_NEW%"
    if errorlevel 1 (
        echo GCC failed. Close %EXE% if running, then retry.
        exit /b 1
    )
    set EXE=%EXE_NEW%
)

echo [3/3] run: %EXE%
echo ---
if "%BASE%"=="test3_generated" (
    echo 10| "%EXE%"
) else (
    "%EXE%"
)
echo ---
echo Done.
