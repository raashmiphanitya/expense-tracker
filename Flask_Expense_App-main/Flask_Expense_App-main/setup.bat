@echo off
echo Setting up Flask Expense App...

REM Set Python path
set PYTHON_PATH=C:\Users\naray\AppData\Local\Programs\Python\Python311\python.exe

REM Install requirements
echo Installing requirements...
"%PYTHON_PATH%" -m pip install -r requirements.txt

REM Run MySQL setup
echo Setting up MySQL...
"%PYTHON_PATH%" setup_mysql.py

REM Run the Flask application
echo Starting Flask application...
"%PYTHON_PATH%" main.py

pause 