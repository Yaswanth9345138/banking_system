from database import (
    get_balance,
    update_balance,
    account_exists,
    add_transaction,
    get_transactions
)


def deposit(account_number, amount):
    """Deposit money into an account."""

    if not account_exists(account_number):
        print("Account does not exist.")
        return False

    if amount <= 0:
        print("Amount must be greater than zero.")
        return False

    balance = get_balance(account_number)

    if balance is None:
        print("Unable to get account balance.")
        return False

    new_balance = balance + amount

    if update_balance(account_number, new_balance):
        add_transaction(
            account_number,
            "DEPOSIT",
            amount,
            "Money deposited"
        )

        print(f"₹{amount:.2f} deposited successfully.")
        print(f"New balance: ₹{new_balance:.2f}")

        return True

    print("Deposit failed.")
    return False


def withdraw(account_number, amount):
    """Withdraw money from an account."""

    if not account_exists(account_number):
        print("Account does not exist.")
        return False

    if amount <= 0:
        print("Amount must be greater than zero.")
        return False

    balance = get_balance(account_number)

    if balance is None:
        print("Unable to get account balance.")
        return False

    if amount > balance:
        print("Insufficient balance.")
        return False

    new_balance = balance - amount

    if update_balance(account_number, new_balance):
        add_transaction(
            account_number,
            "WITHDRAW",
            amount,
            "Money withdrawn"
        )

        print(f"₹{amount:.2f} withdrawn successfully.")
        print(f"New balance: ₹{new_balance:.2f}")

        return True

    print("Withdrawal failed.")
    return False


def transfer(sender_account, receiver_account, amount):
    """Transfer money from one account to another."""

    if not account_exists(sender_account):
        print("Sender account does not exist.")
        return False

    if not account_exists(receiver_account):
        print("Receiver account does not exist.")
        return False

    if sender_account == receiver_account:
        print("Cannot transfer money to the same account.")
        return False

    if amount <= 0:
        print("Amount must be greater than zero.")
        return False

    sender_balance = get_balance(sender_account)
    receiver_balance = get_balance(receiver_account)

    if sender_balance is None or receiver_balance is None:
        print("Unable to get account balance.")
        return False

    if amount > sender_balance:
        print("Insufficient balance.")
        return False

    new_sender_balance = sender_balance - amount
    new_receiver_balance = receiver_balance + amount

    sender_updated = update_balance(
        sender_account,
        new_sender_balance
    )

    if not sender_updated:
        print("Transfer failed.")
        return False

    receiver_updated = update_balance(
        receiver_account,
        new_receiver_balance
    )

    if not receiver_updated:
        # Try to restore sender's balance
        update_balance(sender_account, sender_balance)

        print("Transfer failed.")
        return False

    add_transaction(
        sender_account,
        "TRANSFER_SENT",
        amount,
        f"Transferred to account {receiver_account}"
    )

    add_transaction(
        receiver_account,
        "TRANSFER_RECEIVED",
        amount,
        f"Received from account {sender_account}"
    )

    print(f"₹{amount:.2f} transferred successfully.")
    print(f"New balance: ₹{new_sender_balance:.2f}")

    return True


def show_transactions(account_number):
    """Display transaction history."""

    if not account_exists(account_number):
        print("Account does not exist.")
        return

    transactions = get_transactions(account_number)

    if not transactions:
        print("No transactions found.")
        return

    print("\n========== TRANSACTION HISTORY ==========")

    for transaction in transactions:
        print("-----------------------------------------")
        print(f"ID          : {transaction['transaction_id']}")
        print(f"Type        : {transaction['transaction_type']}")
        print(f"Amount      : ₹{transaction['amount']:.2f}")
        print(f"Description : {transaction['description']}")
        print(f"Date        : {transaction['transaction_date']}")

    print("-----------------------------------------")


def show_summary(account_number):
    """Display a basic financial summary."""

    if not account_exists(account_number):
        print("Account does not exist.")
        return

    transactions = get_transactions(account_number)

    total_deposits = 0
    total_withdrawals = 0
    total_sent = 0
    total_received = 0

    for transaction in transactions:

        transaction_type = transaction["transaction_type"]
        amount = float(transaction["amount"])

        if transaction_type == "DEPOSIT":
            total_deposits += amount

        elif transaction_type == "WITHDRAW":
            total_withdrawals += amount

        elif transaction_type == "TRANSFER_SENT":
            total_sent += amount

        elif transaction_type == "TRANSFER_RECEIVED":
            total_received += amount

    balance = get_balance(account_number)

    print("\n========== FINANCIAL SUMMARY ==========")
    print(f"Total Deposits       : ₹{total_deposits:.2f}")
    print(f"Total Withdrawals    : ₹{total_withdrawals:.2f}")
    print(f"Total Sent           : ₹{total_sent:.2f}")
    print(f"Total Received       : ₹{total_received:.2f}")
    print(f"Current Balance      : ₹{balance:.2f}")
    print("=======================================")