@echo off
echo Running Read_images.py...
python Object-Detection\Read_images.py

echo.
echo Running count.py...
python Simulation\data\count.py

echo.
echo Both scripts have finished executing.
echo.
pause