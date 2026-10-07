CREATE DATABASE IF NOT EXISTS banking_db;

USE banking_db;

-- Existing account table used by account.py
CREATE TABLE IF NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    account_number INT UNIQUE NOT NULL,
    balance DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- New table for Member 2's transactions
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_number INT NOT NULL,
    transaction_type ENUM('DEPOSIT', 'WITHDRAW', 'TRANSFER_SENT', 'TRANSFER_RECEIVED') NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    description VARCHAR(255),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (account_number)
        REFERENCES accounts(account_number)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Index for faster transaction-history queries
CREATE INDEX idx_account_transactions
ON transactions(account_number);