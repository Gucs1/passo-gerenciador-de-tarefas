@echo off
cd /d "%~dp0"
echo Abra http://127.0.0.1:8765 no navegador.
echo Para encerrar, pressione Ctrl+C nesta janela.
python web.py
pause
