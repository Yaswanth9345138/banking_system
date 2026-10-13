""" this is the authentication and user account layer"""
""" we will get users name, email, account no and passwd and see of the user exists or not and return the the data on him to the system"""

import re
import hmac
import hashlib
import mysql.connector
from mysql.connector import Error

# The MySQL login lives in database.py so it only has to be changed in one place.
from database import DB_NAME, DB_CONFIG


def checkmail(email):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    # fullmatch = the WHOLE string must look like an email (and never raises on junk input)
    return re.fullmatch(pattern, email) is not None


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
    Connects to MySQL. If 'banking_db' or its tables do not exist,
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

        # Step 4: Create Transactions table if it doesn't exist
        # (same layout as datatbase.sql, so the app also works if that file was never run)
        create_transactions_query = """
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
        """
        cursor.execute(create_transactions_query)
        conn.commit()
        cursor.close()

        return conn

    except Error as e:
        print(f"Database Initialization Error: {e}")
        return None


def _fail(message, error=None, **extra):
    """Builds the result dictionary returned when something goes wrong."""
    result = {"success": False, "message": message}
    if error:
        result["error"] = error  # "db" = the database is the problem, not the user's input
    result.update(extra)
    return result


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

    # ------------------------------------------------------------------
    # REGISTRATION
    # register_user() does the real work and returns a dictionary.
    # newuser() is the console version: it asks questions, then calls register_user().
    # The Flutter app (through api.py) calls register_user() directly.
    # ------------------------------------------------------------------

    def register_user(self, username, name, email, passwd) -> dict:
        """Registers a new user with auto-incremented account number starting from 1000."""
        username = username.strip()
        name = name.strip()
        email = email.strip()

        # Validation
        if not username or not name:
            return _fail("Username and full name are required.")

        if len(username) > 50 or len(name) > 100 or len(email) > 100:
            return _fail("Username, name or email is too long.")

        if not checkmail(email):
            return _fail("Invalid email format.")

        if not checkpasswd(passwd):
            return _fail(
                "Invalid password. Use at least 6 characters: letters, numbers "
                "and . @ # _ ! $ % ^ & * ( ) + - are allowed."
            )

        conn = get_db_connection()
        if not conn:
            return _fail("Could not connect to the database.", error="db")

        cursor = None
        try:
            cursor = conn.cursor()

            # Check if username already exists
            cursor.execute("SELECT id FROM accounts WHERE username = %s", (username,))
            if cursor.fetchone():
                return _fail("Username already exists.")

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

            return {
                "success": True,
                "message": "Registration successful.",
                "account_number": account_number,
            }

        except Error as e:
            print(f"Database Error during registration: {e}")
            return _fail("Database error during registration. Please try again.", error="db")
        finally:
            if cursor:
                cursor.close()
            conn.close()

    def newuser(self) -> bool:
        """Console registration: asks for the details, then calls register_user()."""
        print("\n--- USER REGISTRATION ---")
        username = input("Enter username: ").strip()
        name = input("Enter full name: ").strip()
        email = input("Enter email: ").strip()
        passwd = input("Enter password (min 6 chars): ").strip()

        result = self.register_user(username, name, email, passwd)

        if result["success"]:
            print("\nRegistration Successful!")
            print(f"Assigned Account Number: {result['account_number']}")
            return True

        print(f"Error: {result['message']}")
        return False

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------

    def login_user(self, username, passwd) -> dict:
        """Authenticates user and retrieves account details."""
        username = username.strip()

        conn = get_db_connection()
        if not conn:
            return _fail("Could not connect to the database.", error="db")

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT password_hash, account_number, name FROM accounts WHERE username = %s"
            cursor.execute(query, (username,))
            user_record = cursor.fetchone()

            # One message for both "no such user" and "wrong password", so nobody can
            # use the login form to find out which usernames exist.
            if not user_record or not hmac.compare_digest(
                user_record["password_hash"], hash_password(passwd)
            ):
                return _fail("Invalid username or password.")

            self.current_user = {
                "username": username,
                "account_number": user_record["account_number"],
                "name": user_record["name"],
            }
            return {
                "success": True,
                "message": f"Welcome back, {user_record['name']}!",
                "user": self.current_user,
            }

        except Error as e:
            print(f"Database Error during login: {e}")
            return _fail("Database error during login. Please try again.", error="db")
        finally:
            if cursor:
                cursor.close()
            conn.close()

    def login(self) -> bool:
        """Console login: asks for username/password, then calls login_user()."""
        print("\n--- LOGIN ---")
        username = input("Enter username: ").strip()
        passwd = input("Enter password: ").strip()

        result = self.login_user(username, passwd)

        if result["success"]:
            print(f"\n{result['message']}")
            print(f"Retrieved Account Number: {self.current_user['account_number']}")
            return True

        print(f"Error: {result['message']}")
        return False

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

        cursor = None
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
                print(f"Current Balance: ₹{user['balance']:.2f}")

        except Error as e:
            print(f"Database Error fetching profile: {e}")
        finally:
            if cursor:
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
