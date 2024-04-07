@echo off
setlocal EnableDelayedExpansion

set "rounds=2"

for /L %%i in (1,1,%rounds%) do (
    echo Round %%i of %rounds%...
    
    echo.
    echo Swapping images...
    python Object-Detection\Swap_images.py
    
    echo.
    echo Running Read_images.py...
    python Object-Detection\Read_images.py
    
    echo.
    echo Running count.py...
    python Simulation\data\count.py
    
    echo.
    echo Round %%i completed.
    echo.
)

echo All rounds have finished executing.
echo.
pause
