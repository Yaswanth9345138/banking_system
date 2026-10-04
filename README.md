# banking_system
python project which uses all OOP , class inheritance , IO concepts



# Banking Management System — Authentication & User Account Layer

Python-based authentication and account management module using **MySQL**.

## Features

* User registration and login
* SHA-256 password hashing
* Email/password validation
* Automatic account-number generation (`1000+`)
* MySQL data persistence
* Parameterized queries

## Architecture

```text
User
 │
 ├── Register ──► Validation ──► Account Creation
 │                                      │
 │                                      ▼
 │                                  MySQL DB
 │
 └── Login ────► Hash Verification ──► Session
```

## Database

The application automatically creates `banking_db` and the `accounts` table.

| Column           | Type          | Description           |
| ---------------- | ------------- | --------------------- |
| `id`             | INT           | Primary key           |
| `username`       | VARCHAR(50)   | Unique username       |
| `name`           | VARCHAR(100)  | Account holder        |
| `email`          | VARCHAR(100)  | Email address         |
| `password_hash`  | VARCHAR(256)  | SHA-256 password hash |
| `account_number` | INT           | Unique account number |
| `balance`        | DECIMAL(12,2) | Account balance       |
| `created_at`     | TIMESTAMP     | Creation time         |

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```powershell
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install mysql-connector-python
```

### 3. Configure MySQL

Create a MySQL user:

```sql
CREATE USER IF NOT EXISTS 'bankuser'@'localhost'
IDENTIFIED BY 'bankpassword123';

GRANT ALL PRIVILEGES ON *.* TO 'bankuser'@'localhost';

FLUSH PRIVILEGES;
```

Update `DB_CONFIG` in `account.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "bankuser",
    "password": "bankpassword123",
}
```

## Run

```bash
python account.py
```

## Usage

```python
from account import Account

bank = Account()

bank.newuser()

if bank.login():
    print(f"Active Account: {bank.get_account_number()}")
    bank.view_profile()
    bank.logout()
```

> **Note:** This is intended as a development/academic project. Production banking systems require stronger password hashing, secret management, encryption, MFA, rate limiting, and proper transaction handling.

