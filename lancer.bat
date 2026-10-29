@echo off
rem Lance l'interface graphique du diagnostic Internet par double-clic
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python application.py
if errorlevel 1 pause