@echo off
setlocal enabledelayedexpansion

:: Drag-and-drop target. For right-click menu, run install_menu.bat instead.

if "%~1"=="" (
    echo.
    echo  Compress Images
    echo  ---------------
    echo  Drag one or more image files onto this script to compress them.
    echo  Supported: JPG, PNG, WEBP, BMP, TIFF
    echo  Originals are overwritten. Files are skipped if already optimal.
    echo.
    pause
    exit /b
)

set "ARGS="
:loop
if "%~1"=="" goto run
set "ARGS=!ARGS! "%~1""
shift
goto loop

:run
python "%~dp0compress_images.py" !ARGS!
