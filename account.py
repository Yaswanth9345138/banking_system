""" this is the authetication and user account layer"""
""" we will get users name, email, account no and passwd and see of the user exists or not and return the the data on him to the system"""

import re
import hashlib
import mysql.connector
from mysql.connector import Error

DB_NAME = "banking_db"
DB_CONFIG = {
    "host": "localhost",
    "user": "bankuser",
    "password": "bankpassword123",
}

def checkmail(email):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    emails = re.findall(pattern,email)

    return emails[0] == email

def checkpasswd(passwd: str) -> bool:
    """Validates password strength (min 6 chars)."""
    if len(passwd) < 6:
        return False
    pattern = r"^[a-zA-Z0-9.@#_!$%^&*()+-]+$"
    return bool(re.match(pattern, passwd))

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_db_connection():
    """
    Connects to MySQL. If 'banking_db' or the 'accounts' table does not exist,
    creates them automatically.
    """
    try:
        # Step 1: Connect to MySQL server without selecting a DB
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Step 2: Create Database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        # Step 3: Create Accounts table if it doesn't exist
        create_table_query = """
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
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()

        return conn

    except Error as e:
        print(f"Database Initialization Error: {e}")
        return None



class Account:


    def __init__(self):
        self.current_user = None



    def _get_next_account_number(self, cursor) -> int:
        """
        Queries MySQL for the maximum existing account_number.
        If no accounts exist, returns 1000.
        Otherwise, returns (MAX(account_number) + 1).
        """
        cursor.execute("SELECT MAX(account_number) FROM accounts")
        max_account = cursor.fetchone()[0]

        if max_account is None:
            return 1000
        return max_account + 1



    def newuser(self) -> bool:
        """Registers a new user with auto-incremented account number starting from 1000."""
        print("\n--- USER REGISTRATION ---")
        username = input("Enter username: ").strip()
        name = input("Enter full name: ").strip()
        email = input("Enter email: ").strip()
        passwd = input("Enter password (min 6 chars): ").strip()

        # Validation
        if not checkmail(email):
            print("Error: Invalid email format.")
            return False

        if not checkpasswd(passwd):
            print("Error: Invalid password format or too short.")
            return False

        conn = get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # Check if username already exists
            cursor.execute("SELECT id FROM accounts WHERE username = %s", (username,))
            if cursor.fetchone():
                print("Error: Username already exists.")
                return False

            # Auto-calculate next account number directly from DB
            account_number = self._get_next_account_number(cursor)
            hashed_pw = hash_password(passwd)

            # Insert new record into database
            insert_query = """
                INSERT INTO accounts (username, name, email, password_hash, account_number, balance)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (username, name, email, hashed_pw, account_number, 0.00))
            conn.commit()

            print(f"\nRegistration Successful!")
            print(f"Assigned Account Number: {account_number}")
            return True

        except Error as e:
            print(f"Database Error during registration: {e}")
            return False
        finally:
            cursor.close()
            conn.close()



    def login(self) -> bool:
        """Authenticates user and retrieves account details."""
        print("\n--- LOGIN ---")
        username = input("Enter username: ").strip()
        passwd = input("Enter password: ").strip()

        conn = get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT password_hash, account_number, name FROM accounts WHERE username = %s"
            cursor.execute(query, (username,))
            user_record = cursor.fetchone()

            if not user_record:
                print("Error: Username not found.")
                return False

            if user_record["password_hash"] == hash_password(passwd):
                self.current_user = {
                    "username": username,
                    "account_number": user_record["account_number"],
                    "name": user_record["name"]
                }
                print(f"\nWelcome back, {user_record['name']}!")
                print(f"Retrieved Account Number: {user_record['account_number']}")
                return True
            else:
                print("Error: Incorrect password.")
                return False

        except Error as e:
            print(f"Database Error during login: {e}")
            return False
        finally:
            cursor.close()
            conn.close()



    def logout(self) -> bool:
        """Logs out active user session."""
        if self.current_user:
            print(f"User '{self.current_user['username']}' logged out.")
            self.current_user = None
            return True
        print("No active session.")
        return False



    def get_account_number(self):
        """Returns the logged-in user's account number."""
        if not self.current_user:
            print("Error: Please log in first.")
            return None
        return self.current_user["account_number"]



    def view_profile(self):
        """Fetches and displays current user profile."""
        if not self.current_user:
            print("Error: Please log in first.")
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT username, name, email, account_number, balance FROM accounts WHERE username = %s"
            cursor.execute(query, (self.current_user["username"],))
            user = cursor.fetchone()

            if user:
                print("\n--- USER PROFILE ---")
                print(f"Username:       {user['username']}")
                print(f"Full Name:      {user['name']}")
                print(f"Email:          {user['email']}")
                print(f"Account Number: {user['account_number']}")
                print(f"Current Balance:${user['balance']:.2f}")

        except Error as e:
            print(f"Database Error fetching profile: {e}")
        finally:
            cursor.close()
            conn.close()
        


#test case
if __name__ == "__main__":
    bank = Account()

    # Step 1: Register new user (Will auto-initialize DB if missing)
    bank.newuser()

    # Step 2: Login and check retrieved account number
    if bank.login():
        print(f"Active Account Number: {bank.get_account_number()}")
        bank.view_profile()
        bank.logout()
