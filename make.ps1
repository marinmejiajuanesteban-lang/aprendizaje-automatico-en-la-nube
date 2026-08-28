# Wrapper para 'make' en Windows: usa 'make' si ya esta en el PATH del sistema,
# y si no lo encuentra, cae a la ruta tipica de la instalacion de GnuWin32 Make.

$makeCmd = Get-Command make -ErrorAction SilentlyContinue

if ($makeCmd) {
    & $makeCmd.Source @args
}
elseif (Test-Path "C:\Program Files (x86)\GnuWin32\bin\make.exe") {
    & "C:\Program Files (x86)\GnuWin32\bin\make.exe" @args
}
else {
    Write-Host "No se encontro 'make'. Instalalo con: winget install GnuWin32.Make" -ForegroundColor Red
    exit 1
}