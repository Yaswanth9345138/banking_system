"""
api.py  -  the web API that the Flutter app talks to.

Flutter app  --(HTTP + JSON)-->  api.py  -->  account.py / transactions.py  -->  database.py  -->  MySQL

This file contains NO banking rules of its own. It receives a request, checks the
user is logged in, calls the same functions the console menu (main.py) uses, and
sends the result back as JSON.

Run it with:   uvicorn api:app --reload
Try it in the browser (auto-generated docs):   http://127.0.0.1:8000/docs
"""

import secrets
import sys
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from account import Account, get_db_connection
from database import (
    account_exists,
    get_account,
    get_balance,
    get_transactions
)
from transactions import (
    deposit,
    withdraw,
    transfer
)

# transactions.py prints the rupee sign; make sure that never crashes on a non-UTF-8 console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once when the server starts: make sure the database and tables exist."""
    conn = get_db_connection()

    if conn:
        conn.close()
        print("Database ready.")
    else:
        print("WARNING: could not connect to MySQL. Check DB_CONFIG in database.py.")

    yield


app = FastAPI(title="Banking System API", lifespan=lifespan)

# Lets the Flutter *web* build (running on another port) call this API.
# Safe here because we authenticate with a token header, not cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- SESSIONS ----------
# Every successful login gets its own random token. The app sends it back on every
# request as   Authorization: Bearer <token>   so many users can be logged in at once.
# (Kept in memory, so restarting the server logs everybody out.)

sessions = {}

# One transaction can't be bigger than this (the DB column holds 12 digits in total)
MAX_AMOUNT = Decimal("10000000")


def get_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Please login first.")

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or token not in sessions:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in again."
        )

    return token


def current_user(token: str = Depends(get_token)) -> dict:
    """Dependency used by every protected endpoint: returns the logged-in user."""
    return sessions[token]


def valid_amount(amount: Decimal) -> Decimal:
    """Checks an amount from the app and returns it, or raises a clear error."""

    if not amount.is_finite():
        raise HTTPException(status_code=400, detail="Enter a valid amount.")

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero."
        )

    if amount.as_tuple().exponent < -2:
        raise HTTPException(
            status_code=400,
            detail="Amount can have at most 2 decimal places."
        )

    if amount > MAX_AMOUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Amount cannot be more than ₹{MAX_AMOUNT:,.2f} in one transaction."
        )

    return amount


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

    result = Account().register_user(
        request.username,
        request.name,
        request.email,
        request.password
    )

    if not result["success"]:
        status = 503 if result.get("error") == "db" else 400
        raise HTTPException(status_code=status, detail=result["message"])

    return result


@app.post("/login")
def login(request: LoginRequest):

    account = Account()

    result = account.login_user(
        request.username,
        request.password
    )

    if not result["success"]:
        status = 503 if result.get("error") == "db" else 401
        raise HTTPException(status_code=status, detail=result["message"])

    token = secrets.token_urlsafe(32)
    sessions[token] = account.current_user

    return {
        "success": True,
        "message": result["message"],
        "token": token,
        "user": account.current_user
    }


@app.post("/logout")
def logout(token: str = Depends(get_token)):

    user = sessions.pop(token)

    return {
        "success": True,
        "message": f"User '{user['username']}' logged out."
    }


# ---------- PROFILE ----------

@app.get("/profile")
def profile(user: dict = Depends(current_user)):

    account_number = user["account_number"]

    details = get_account(account_number)

    if not details:
        raise HTTPException(
            status_code=404,
            detail="Account not found."
        )

    return {
        "username": details["username"],
        "name": details["name"],
        "email": details["email"],
        "account_number": details["account_number"],
        "balance": str(details["balance"])
    }


# ---------- BALANCE ----------

@app.get("/balance")
def balance(user: dict = Depends(current_user)):

    account_number = user["account_number"]

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
def make_deposit(request: AmountRequest, user: dict = Depends(current_user)):

    account_number = user["account_number"]

    amount = valid_amount(request.amount)

    if not deposit(account_number, amount):
        raise HTTPException(
            status_code=400,
            detail="Deposit failed. Please try again."
        )

    return {
        "success": True,
        "message": "Money deposited successfully.",
        "amount": str(amount),
        "balance": str(get_balance(account_number))
    }


# ---------- WITHDRAW ----------

@app.post("/withdraw")
def make_withdrawal(request: AmountRequest, user: dict = Depends(current_user)):

    account_number = user["account_number"]

    amount = valid_amount(request.amount)

    current_balance = get_balance(account_number)

    if current_balance is None:
        raise HTTPException(status_code=404, detail="Account not found.")

    # Checked here as well so the app can show the real reason, not just "failed"
    if amount > current_balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. You have ₹{current_balance:,.2f}."
        )

    if not withdraw(account_number, amount):
        raise HTTPException(
            status_code=400,
            detail="Withdrawal failed. Please try again."
        )

    return {
        "success": True,
        "message": "Money withdrawn successfully.",
        "amount": str(amount),
        "balance": str(get_balance(account_number))
    }


# ---------- TRANSFER ----------

@app.post("/transfer")
def make_transfer(request: TransferRequest, user: dict = Depends(current_user)):

    sender_account = user["account_number"]

    amount = valid_amount(request.amount)

    if request.receiver_account == sender_account:
        raise HTTPException(
            status_code=400,
            detail="You cannot send money to your own account."
        )

    if not account_exists(request.receiver_account):
        raise HTTPException(
            status_code=404,
            detail=f"Account {request.receiver_account} does not exist."
        )

    current_balance = get_balance(sender_account)

    if current_balance is None:
        raise HTTPException(status_code=404, detail="Account not found.")

    if amount > current_balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. You have ₹{current_balance:,.2f}."
        )

    if not transfer(sender_account, request.receiver_account, amount):
        raise HTTPException(
            status_code=400,
            detail="Transfer failed. Please try again."
        )

    return {
        "success": True,
        "message": "Money transferred successfully.",
        "receiver_account": request.receiver_account,
        "amount": str(amount),
        "balance": str(get_balance(sender_account))
    }


# ---------- TRANSACTIONS ----------

@app.get("/transactions")
def transactions(user: dict = Depends(current_user)):

    account_number = user["account_number"]

    transaction_list = get_transactions(account_number)

    # Convert Decimal and datetime into JSON-friendly values
    for transaction in transaction_list:
        transaction["amount"] = str(transaction["amount"])
        transaction["transaction_date"] = transaction["transaction_date"].isoformat()

    return {
        "account_number": account_number,
        "transactions": transaction_list
    }


# ---------- SUMMARY ----------

@app.get("/summary")
def summary(user: dict = Depends(current_user)):

    account_number = user["account_number"]

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


# ---------- EXPORT (file handling) ----------
# Writes the statement to a real .txt file on the server (file I/O), then sends it back.

EXPORT_DIR = Path(__file__).resolve().parent / "exports"


@app.get("/export")
def export_transactions(user: dict = Depends(current_user)):

    account_number = user["account_number"]

    transaction_list = get_transactions(account_number)

    if not transaction_list:
        raise HTTPException(
            status_code=404,
            detail="No transactions found."
        )

    EXPORT_DIR.mkdir(exist_ok=True)

    filename = f"transactions_{account_number}.txt"
    file_path = EXPORT_DIR / filename

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
