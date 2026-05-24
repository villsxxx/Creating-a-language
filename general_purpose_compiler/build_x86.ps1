param(
    [string]$Asm = "generated\test2_generated.asm"
)

$ErrorActionPreference = "Stop"
$Base = [System.IO.Path]::GetFileNameWithoutExtension($Asm)
$Obj = "generated\$Base.obj"
$Exe = "generated\$Base.exe"

Write-Host "[1/3] nasm: $Asm"
& nasm -f win64 $Asm -o $Obj
if ($LASTEXITCODE -ne 0) {
    Write-Host "NASM failed. Install NASM and reopen terminal."
    exit 1
}

Write-Host "[2/3] gcc: $Exe"
if (Test-Path $Exe) { Remove-Item -Force $Exe -ErrorAction SilentlyContinue }
& gcc -no-pie $Obj -o $Exe
if ($LASTEXITCODE -ne 0) {
    $Exe = "generated\${Base}_new.exe"
    Write-Host "Retrying as $Exe ..."
    & gcc -no-pie $Obj -o $Exe
    if ($LASTEXITCODE -ne 0) {
        Write-Host "GCC failed. Close running $Base.exe, then retry."
        exit 1
    }
}

Write-Host "[3/3] run: $Exe"
Write-Host "---"
if ($Base -eq "test3_generated") {
    "10" | & $Exe
} else {
    & $Exe
}
Write-Host "---"
Write-Host "Done."
