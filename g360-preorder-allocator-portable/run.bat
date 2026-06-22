@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

set LOG_FILE=run_log.txt
echo [%DATE% %TIME%] Inicio > %LOG_FILE%

echo.
echo ========================================
echo    G360 PreOrder Allocator
echo    Analisis de compras y participacion por SKU
echo ========================================
echo.

REM ============================================
REM [1/5] Verificar / Instalar uv
echo [%DATE% %TIME%] [1/5] Verificando uv... >> %LOG_FILE%
echo [1/5] Verificando uv...

where uv >nul 2>&1
if errorlevel 1 (
    if exist "uv.exe" (
        echo   Usando uv.exe local...
        set "PATH=%~dp0;%PATH%"
    ) else (
        echo   uv no encontrado. Instalando...
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" >> %LOG_FILE% 2>&1
        if errorlevel 1 (
            echo [%DATE% %TIME%] [ERROR] No se pudo instalar uv >> %LOG_FILE%
            echo   ERROR: No se pudo instalar uv.
            msg * "PreOrder Allocator: No se pudo instalar uv. Descarguelo de https://docs.astral.sh/uv/"
            pause
            exit /b 1
        )
        echo   uv instalado.
    )
) else (
    echo   uv encontrado.
)

for /f "tokens=*" %%i in ('where uv 2^>nul') do set "UV_PATH=%%~dpi"
if defined UV_PATH set "PATH=!UV_PATH!;%PATH%"

where uv >nul 2>&1
if errorlevel 1 (
    if exist "%USERPROFILE%\.cargo\bin\uv.exe" (
        set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    ) else if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    )
)

echo.

REM ============================================
REM [2/5] Verificar / Instalar Python 3.11
echo [%DATE% %TIME%] [2/5] Verificando Python... >> %LOG_FILE%
echo [2/5] Verificando Python...

uv python list --only-installed 2>nul | find "3.11" >nul
if errorlevel 1 (
    echo   Python 3.11 no encontrado. Instalando...
    uv python install 3.11 >> %LOG_FILE% 2>&1
    if errorlevel 1 (
        echo [%DATE% %TIME%] [ERROR] No se pudo instalar Python 3.11 >> %LOG_FILE%
        echo   ERROR: No se pudo instalar Python 3.11.
        msg * "PreOrder Allocator: No se pudo instalar Python 3.11. Revise %LOG_FILE%"
        pause
        exit /b 1
    )
    echo   Python 3.11 instalado.
) else (
    echo   Python 3.11 encontrado.
)

echo.

REM ============================================
REM [3/5] Entorno virtual y dependencias
echo [%DATE% %TIME%] [3/5] Configurando entorno... >> %LOG_FILE%
echo [3/5] Configurando entorno virtual...

if not exist ".venv\Scripts\python.exe" (
    echo   Creando entorno virtual...
    uv venv .venv --python 3.11 --seed >> %LOG_FILE% 2>&1
    if errorlevel 1 (
        echo [%DATE% %TIME%] [ERROR] No se pudo crear .venv >> %LOG_FILE%
        echo   ERROR: No se pudo crear el entorno virtual.
        msg * "PreOrder Allocator: No se pudo crear .venv. Revise %LOG_FILE%"
        pause
        exit /b 1
    )
    echo   Entorno virtual creado.
) else (
    .venv\Scripts\python.exe -c "import sys" 2>> %LOG_FILE%
    if errorlevel 1 (
        echo   .venv corrupto, recreando...
        rd /s /q ".venv" 2>> %LOG_FILE%
        uv venv .venv --python 3.11 --seed >> %LOG_FILE% 2>&1
    )
)

echo   Instalando dependencias...
uv sync >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [%DATE% %TIME%] [ERROR] Error en dependencias >> %LOG_FILE%
    echo   ERROR: No se pudieron instalar las dependencias.
    msg * "PreOrder Allocator: Error en dependencias. Revise %LOG_FILE%"
    pause
    exit /b 1
)
echo [%DATE% %TIME%] [3/5] Dependencias listas >> %LOG_FILE%
echo   Dependencias instaladas.

echo.

REM ============================================
REM [4/5] Acceso directo en escritorio
echo [%DATE% %TIME%] [4/5] Acceso directo... >> %LOG_FILE%
echo [4/5] Creando acceso directo...

if not exist "%USERPROFILE%\Desktop\PreOrder Allocator.lnk" (
    if exist "create_shortcut.vbs" (
        cscript //nologo create_shortcut.vbs >> %LOG_FILE% 2>&1
        echo   Acceso directo creado en el escritorio.
    ) else (
        echo   create_shortcut.vbs no encontrado.
    )
) else (
    echo   Acceso directo ya existe.
)

echo.

REM ============================================
REM [5/5] Iniciar aplicacion
echo [%DATE% %TIME%] [5/5] Iniciando PreOrder Allocator... >> %LOG_FILE%
echo [5/5] Iniciando aplicacion...
echo.

.venv\Scripts\python.exe main.py

if errorlevel 1 (
    echo [%DATE% %TIME%] [ERROR] La aplicacion fallo >> %LOG_FILE%
    echo.
    echo La aplicacion fallo. Revise %LOG_FILE% para mas detalles.
    msg * "PreOrder Allocator: La aplicacion fallo. Revise %LOG_FILE%"
    pause
)

echo [%DATE% %TIME%] App terminada >> %LOG_FILE%
echo.
echo ========================================
