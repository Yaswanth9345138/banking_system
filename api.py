from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from decimal import Decimal
from pathlib import Path

from account import Account
from database import (
    get_balance,
    get_account,
    get_transactions
)
from transactions import (
    deposit,
    withdraw,
    transfer
)


app = FastAPI(title="Banking System API")

bank = Account()


# ---------- REQUEST MODELS ----------

class RegisterRequest(BaseModel):
    username: str
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AmountRequest(BaseModel):
    amount: Decimal


class TransferRequest(BaseModel):
    receiver_account: int
    amount: Decimal


# ---------- BASIC ----------

@app.get("/")
def home():
    return {"message": "Banking System API is running"}


# ---------- AUTHENTICATION ----------

@app.post("/register")
def register(request: RegisterRequest):

    result = bank.register_user(
        request.username,
        request.name,
        request.email,
        request.password
    )

    return result


@app.post("/login")
def login(request: LoginRequest):

    result = bank.login_user(
        request.username,
        request.password
    )

    return result


@app.post("/logout")
def logout():

    if not bank.current_user:
        return {
            "success": False,
            "message": "No active session."
        }

    username = bank.current_user["username"]

    bank.logout()

    return {
        "success": True,
        "message": f"User '{username}' logged out."
    }


# ---------- PROFILE ----------

@app.get("/profile")
def profile():

    if not bank.current_user:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )

    account_number = bank.current_user["account_number"]

    user = get_account(account_number)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Account not found."
        )

    return {
        "username": user["username"],
        "name": user["name"],
        "email": user["email"],
        "account_number": user["account_number"],
        "balance": str(user["balance"])
    }


# ---------- BALANCE ----------

@app.get("/balance")
def balance():

    if not bank.current_user:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )

    account_number = bank.current_user["account_number"]

    current_balance = get_balance(account_number)

    if current_balance is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found."
        )

    return {
        "account_number": account_number,
        "balance": str(current_balance)
    }


# ---------- DEPOSIT ----------

@app.post("/deposit")
def make_deposit(request: AmountRequest):

    if not bank.current_user:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )

    account_number = bank.current_user["account_number"]

    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero."
        )

    success = deposit(
        account_number,
        request.amount
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Deposit failed."
        )

    new_balance = get_balance(account_number)

    return {
        "success": True,
        "message": "Money deposited successfully.",
        "amount": str(request.amount),
        "balance": str(new_balance)
    }


# ---------- WITHDRAW ----------

@app.post("/withdraw")
def make_withdrawal(request: AmountRequest):

    if not bank.current_user:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )

    account_number = bank.current_user["account_number"]

    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero."
        )

    success = withdraw(
        account_number,
        request.amount
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Withdrawal failed. Check your balance."
        )

    new_balance = get_balance(account_number)

    return {
        "success": True,
        "message": "Money withdrawn successfully.",
        "amount": str(request.amount),
        "balance": str(new_balance)
    }


# ---------- TRANSFER ----------

@app.post("/transfer")
def make_transfer(request: TransferRequest):

    if not bank.current_user:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )

    sender_account = bank.current_user["account_number"]

    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero."
        )

    success = transfer(
        sender_account,
        request.receiver_account,
        request.amount
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Transfer failed."
        )

    new_balance = get_balance(sender_account)

    return {
        "success": True,
        "message": "Money transferred successfully.",
        "receiver_account": request.receiver_account,
        "amount": str(request.amount),
        "balance": str(new_balance)
    }


# ---------- TRANSACTIONS ----------

@app.get("/transactions")
def transactions():

    if not bank.current_user:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )

    account_number = bank.current_user["account_number"]

    transaction_list = get_transactions(account_number)

    # Convert Decimal and datetime into JSON-friendly values
    for transaction in transaction_list:
        transaction["amount"] = str(transaction["amount"])
        transaction["transaction_date"] = str(
            transaction["transaction_date"]
        )

    return {
        "account_number": account_number,
        "transactions": transaction_list
    }


# ---------- SUMMARY ----------

@app.get("/summary")
def summary():

    if not bank.current_user:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )

    account_number = bank.current_user["account_number"]

    transaction_list = get_transactions(account_number)

    total_deposits = Decimal("0")
    total_withdrawals = Decimal("0")
    total_sent = Decimal("0")
    total_received = Decimal("0")

    for transaction in transaction_list:

        transaction_type = transaction["transaction_type"]
        amount = transaction["amount"]

        if transaction_type == "DEPOSIT":
            total_deposits += amount

        elif transaction_type == "WITHDRAW":
            total_withdrawals += amount

        elif transaction_type == "TRANSFER_SENT":
            total_sent += amount

        elif transaction_type == "TRANSFER_RECEIVED":
            total_received += amount

    current_balance = get_balance(account_number)

    return {
        "total_deposits": str(total_deposits),
        "total_withdrawals": str(total_withdrawals),
        "total_sent": str(total_sent),
        "total_received": str(total_received),
        "current_balance": str(current_balance)
    }


# ---------- EXPORT ----------

@app.get("/export")
def export_transactions():

    if not bank.current_user:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )

    account_number = bank.current_user["account_number"]

    transaction_list = get_transactions(account_number)

    if not transaction_list:
        raise HTTPException(
            status_code=404,
            detail="No transactions found."
        )

    filename = f"transactions_{account_number}.txt"
    file_path = Path(filename)

    with open(file_path, "w", encoding="utf-8") as file:

        file.write("========== TRANSACTION HISTORY ==========\n\n")

        for transaction in transaction_list:

            file.write("-----------------------------------------\n")
            file.write(
                f"ID          : {transaction['transaction_id']}\n"
            )
            file.write(
                f"Type        : {transaction['transaction_type']}\n"
            )
            file.write(
                f"Amount      : ₹{transaction['amount']:.2f}\n"
            )
            file.write(
                f"Description : {transaction['description']}\n"
            )
            file.write(
                f"Date        : {transaction['transaction_date']}\n"
            )

        file.write("-----------------------------------------\n")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/plain"
    )