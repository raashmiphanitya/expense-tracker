CREATE DATABASE IF NOT EXISTS expense;
USE expense;

CREATE TABLE IF NOT EXISTS user_login (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(30) NOT NULL,
    email VARCHAR(30) NOT NULL UNIQUE,
    password VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pdate DATE NOT NULL,
    expense VARCHAR(10) NOT NULL,
    amount INT NOT NULL,
    pdescription VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES user_login(user_id)
); 