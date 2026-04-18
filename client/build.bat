@echo off
:: Install requirements
python -m pip install -r requirements.txt

:: Build executable using PyInstaller
:: -F: One file
:: -w: Windowed (no console)
:: -n: Name of the output executable
python -m PyInstaller -F -w -n PCInfoCollector main.py

echo Build finished! Check the "dist" folder.
pause