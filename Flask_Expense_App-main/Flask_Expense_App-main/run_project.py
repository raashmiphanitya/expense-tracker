import subprocess
import sys
import os
import time
import mysql.connector
from mysql.connector import Error

def install_requirements():
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def setup_database():
    print("Setting up database...")
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Sami@4321"
        )
        cursor = conn.cursor()

        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS expense")
        cursor.execute("USE expense")

        # Create user_login table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_login (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(30) NOT NULL,
                email VARCHAR(30) NOT NULL UNIQUE,
                password VARCHAR(20) NOT NULL
            )
        """)

        # Create user_expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                pdate DATE NOT NULL,
                expense VARCHAR(10) NOT NULL,
                amount INT NOT NULL,
                pdescription VARCHAR(50),
                FOREIGN KEY (user_id) REFERENCES user_login(user_id)
            )
        """)

        conn.commit()
        print("Database and tables created successfully!")
    except Error as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def run_flask_app():
    print("Starting Flask application...")
    try:
        # Run the Flask application
        subprocess.check_call([sys.executable, "main.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error running Flask application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting project setup...")
    install_requirements()
    setup_database()
    run_flask_app() 