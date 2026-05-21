@echo off
setlocal

echo Removing "Compress Image(s)" right-click menu...

set "KEY=HKCU\Software\Classes\SystemFileAssociations\image\shell\CompressImages"

reg delete "%KEY%" /f >nul 2>&1

if %errorlevel% == 0 (
    echo Done. Menu item removed.
) else (
    echo Nothing to remove ^(menu item was not installed^).
)

echo.
pause
