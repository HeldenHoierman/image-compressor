@echo off
setlocal

echo Installing "Compress Image(s)" right-click menu...

:: Resolve pythonw.exe path from the active Python install
for /f "usebackq delims=" %%i in (`python -c "import sys,os;print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"`) do set "PYTHONW=%%i"

if not exist "%PYTHONW%" (
    echo ERROR: pythonw.exe not found at "%PYTHONW%"
    echo Make sure Python is installed and on your PATH.
    pause
    exit /b 1
)

:: Script lives next to this .bat file
set "SCRIPT=%~dp0compress_images.py"

if not exist "%SCRIPT%" (
    echo ERROR: compress_images.py not found at "%SCRIPT%"
    pause
    exit /b 1
)

set "KEY=HKCU\Software\Classes\SystemFileAssociations\image\shell\CompressImages"

:: Menu label
reg add "%KEY%" /ve /d "Compress Image(s)" /f >nul

:: Show for both single and multi-file selections
reg add "%KEY%" /v "MultiSelectModel" /d "Document" /f >nul

:: Use the Python icon
reg add "%KEY%" /v "Icon" /d "\"%PYTHONW%\",0" /f >nul

:: Command — silent flag suppresses all output and the console window
reg add "%KEY%\command" /ve /d "\"%PYTHONW%\" \"%SCRIPT%\" --silent \"%%1\"" /f >nul

echo.
echo Done. Right-click any image file to see "Compress Image(s)".
echo To remove, run uninstall_menu.bat.
echo.
pause
