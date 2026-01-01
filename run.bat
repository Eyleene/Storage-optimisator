@echo off
chcp 65001 > nul
echo ===================================================
echo  Запуск Системи Автоматизації Складу (Warehouse)
echo ===================================================

if not exist "venv" (
    echo [INFO] Створення віртуального середовища...
    python -m venv venv
)

echo [INFO] Активація venv...
call venv\Scripts\activate

echo [INFO] Перевірка залежностей...
pip install -r requirements.txt

echo [INFO] Запуск сервера...
python app.py

pause
