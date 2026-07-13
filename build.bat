@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Building Universal Video Downloader into a single EXE...
pyinstaller --noconsole --onefile --collect-all customtkinter --name "UniversalVideoDownloader" main.py

echo Build complete! Check the "dist" folder.
pause
