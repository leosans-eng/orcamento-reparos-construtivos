@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0.."
set "EXITCODE=0"

call "%~dp0create_exe.bat" nopause
if errorlevel 1 (
    set "EXITCODE=1"
    goto :fim
)

for /f "delims=" %%V in ('".venv\Scripts\python.exe" setup\read_app_version.py') do set "APPVER=%%V"

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if "%ISCC%"=="" (
    echo Inno Setup 6 nao encontrado. Instale em https://jrsoftware.org/isinfo.php
    echo O .exe esta em dist\ORC\ORC.exe
    set "EXITCODE=1"
    goto :fim
)

echo.
echo Gerando instalador...
"%ISCC%" /DMyAppVersion=%APPVER% setup\orc_installer.iss
if errorlevel 1 (
    echo ERRO ao compilar o instalador com Inno Setup.
    echo Se aparecer "EndUpdateResource failed", exclua setup\output do antivirus.
    set "EXITCODE=1"
    goto :fim
)

echo.
echo Concluido:
echo   dist\ORC\ORC.exe
echo   setup\output\ORC_Instalador_%APPVER%.exe
echo.
echo Atualize version.json no GitHub com versao=%APPVER% e o link do instalador.

:fim
if not "%EXITCODE%"=="0" (
    echo.
    echo orc_installer.bat falhou.
) else (
    echo.
    echo Build concluido com sucesso.
)
echo.
pause
exit /b %EXITCODE%
