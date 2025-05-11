import pymysql
from pymysql import Error

def setup_mysql():
    try:
        # First connect without database
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="Sami@4321",
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # Create database if it doesn't exist
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

        # Update root user authentication
        try:
            cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Sami@4321'")
            cursor.execute("FLUSH PRIVILEGES")
        except Error as e:
            print(f"Note: {e}")

        conn.commit()
        print("MySQL setup completed successfully!")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.open:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_mysql() 