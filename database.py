import mysql.connector
from mysql.connector import Error


DB_NAME = "banking_db"

DB_CONFIG = {
    "host": "localhost",
    "user": "bankuser",
    "password": "bankpassword123",
}


def connect_db():
    """
    Connect to the banking_db database.
    """

    try:
        conn = mysql.connector.connect(
            database=DB_NAME,
            **DB_CONFIG
        )

        return conn

    except Error as e:
        print(f"Database connection error: {e}")
        return None


def get_account(account_number):
    """
    Get account details using account number.
    """

    conn = connect_db()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT *
        FROM accounts
        WHERE account_number = %s
        """

        cursor.execute(query, (account_number,))

        return cursor.fetchone()

    except Error as e:
        print(f"Error fetching account: {e}")
        return None

    finally:
        cursor.close()
        conn.close()


def get_balance(account_number):
    """
    Get current balance of an account.
    """

    conn = connect_db()

    if not conn:
        return None

    cursor = conn.cursor()

    try:
        query = """
        SELECT balance
        FROM accounts
        WHERE account_number = %s
        """

        cursor.execute(query, (account_number,))

        result = cursor.fetchone()

        if result:
            return result[0]

        return None

    except Error as e:
        print(f"Error fetching balance: {e}")
        return None

    finally:
        cursor.close()
        conn.close()


def update_balance(account_number, new_balance):
    """
    Update the balance of an account.
    """

    conn = connect_db()

    if not conn:
        return False

    cursor = conn.cursor()

    try:
        query = """
        UPDATE accounts
        SET balance = %s
        WHERE account_number = %s
        """

        cursor.execute(query, (new_balance, account_number))

        conn.commit()

        return cursor.rowcount > 0

    except Error as e:
        print(f"Error updating balance: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def add_transaction(
    account_number,
    transaction_type,
    amount,
    description=""
):
    """
    Store a transaction in the transactions table.
    """

    conn = connect_db()

    if not conn:
        return False

    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO transactions
        (account_number, transaction_type, amount, description)
        VALUES (%s, %s, %s, %s)
        """

        values = (
            account_number,
            transaction_type,
            amount,
            description
        )

        cursor.execute(query, values)

        conn.commit()

        return True

    except Error as e:
        print(f"Error adding transaction: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def get_transactions(account_number):
    """
    Get all transactions belonging to an account.
    """

    conn = connect_db()

    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT
            transaction_id,
            transaction_type,
            amount,
            description,
            transaction_date
        FROM transactions
        WHERE account_number = %s
        ORDER BY transaction_date DESC
        """

        cursor.execute(query, (account_number,))

        return cursor.fetchall()

    except Error as e:
        print(f"Error fetching transactions: {e}")
        return []

    finally:
        cursor.close()
        conn.close()


def account_exists(account_number):
    """
    Check whether an account exists.
    """

    conn = connect_db()

    if not conn:
        return False

    cursor = conn.cursor()

    try:
        query = """
        SELECT account_number
        FROM accounts
        WHERE account_number = %s
        """

        cursor.execute(query, (account_number,))

        return cursor.fetchone() is not None

    except Error as e:
        print(f"Error checking account: {e}")
        return False

    finally:
        cursor.close()
        conn.close()