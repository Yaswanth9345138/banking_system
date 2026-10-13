# Code walkthrough and demo script

## Part 1 - What we wrote and what each part does

### The big picture

```
Flutter app  ->  api.py  ->  account.py / transactions.py  ->  database.py  ->  MySQL
main.py (console) ----------^
```

Each layer has one job and only talks to the layer below it. That is why the same banking
rules serve both the console menu and the Flutter app.

### `database.py` - talks to MySQL

Every SQL query lives here and nowhere else. Functions: `connect_db`, `get_account`,
`get_balance`, `update_balance`, `add_transaction`, `get_transactions`, `account_exists`.
All queries use `%s` placeholders (parameterized), which prevents SQL injection.
`DB_CONFIG` holds the MySQL login.

### `account.py` - users and login

* `checkmail`, `checkpasswd` - validate input with regular expressions.
* `hash_password` - SHA-256, so passwords are never stored as plain text.
* `get_db_connection` - connects and creates `banking_db` and the tables if missing.
* **class `Account`** (OOP): holds the logged-in user in `self.current_user`.
  * `register_user` / `login_user` - the real logic; return a dictionary (`success`, `message`, ...).
  * `newuser` / `login` - console versions: ask with `input()`, then call the two above.
  * `logout`, `get_account_number`, `view_profile`.
* Account numbers: `MAX(account_number) + 1`, starting at 1000.

### `transactions.py` - money rules

`deposit`, `withdraw`, `transfer` each check: account exists, amount > 0, enough balance
(withdraw/transfer). Then they update the balance and write a row to the `transactions` table.
`show_transactions` and `show_summary` print the history and totals.
Money uses `Decimal`, not `float`, so there are no rounding errors (0.1 + 0.2 problem).

### `main.py` - console menu

Two loops: a start menu (register / login / exit) and a logged-in menu (deposit, withdraw,
transfer, balance, history, summary, profile, logout). Bad input is caught with `try/except`.

### `api.py` - the web API for Flutter

Built with FastAPI. It contains no banking rules; it checks the login token, calls the
functions above, and returns JSON.
* Each login creates a random token (`secrets.token_urlsafe`) stored in the `sessions` dict.
* Request classes (`RegisterRequest`, `AmountRequest`, ...) inherit from Pydantic's `BaseModel`
  and validate incoming JSON automatically.
* `/export` writes the statement to a real `.txt` file (file I/O) and returns it.

### `bank_app/` - the Flutter front end

| File | Job |
| --- | --- |
| `lib/main.dart` | Starts the app, applies the theme |
| `lib/api_service.dart` | The only code that makes HTTP calls to the Python API |
| `lib/models.dart` | Classes for profile, transaction, summary (parse the JSON) |
| `lib/format.dart` | Shows money as `₹1,00,000.00` and dates readably |
| `lib/theme.dart` | Colors: ink-blue cover, green = money in, red = money out |
| `lib/screens/login_screen.dart` | Sign in / register / server address |
| `lib/screens/home_screen.dart` | Loads data, runs deposit / withdraw / send |
| `lib/screens/tabs.dart` | Account, History and Profile tabs |
| `lib/widgets/` | Ledger rows, amount dialog, statement dialog, message bar |

### Concepts to mention

* **OOP:** `Account` class (encapsulation), Pydantic models inherit `BaseModel`.
* **File I/O:** statement export; console input/output.
* **Exceptions:** `try/except` for bad input and database errors.
* **Database:** MySQL, parameterized queries, foreign key between `transactions` and `accounts`.
* **Regular expressions:** email and password validation.
* **Modules / layers:** each file has one responsibility.

## Part 2 - Live demo script (about 4 minutes)

Before you start: MySQL running, `uvicorn api:app --reload` running, Flutter app open.

1. **Register** two users, e.g. `asha` and `ben`. Note the account numbers (1000 and 1001).
2. **Sign in as asha.** Show the balance is ₹0.00.
3. **Deposit** 5000. Balance and *Latest entries* update.
4. **Withdraw** 1200. Then try to withdraw 99999 and show the "Insufficient balance" message.
5. **Send money** 800 to account 1001. Try sending to 9999 to show the error.
6. Open **History** and show the ledger, then **Export statement**.
7. **Log out, sign in as ben.** Balance is ₹800 and the entry says "Money received".
8. Show the same data from Python: run `python main.py`, log in as asha and open
   *Transaction History* - same numbers, because both use the same code and database.
9. Optional: open <http://127.0.0.1:8000/docs> to show the API.

## Likely questions - honest answers

* **Why SHA-256?** It hides plain passwords, but a real bank would use a salted, slow hash such as bcrypt.
* **Is a transfer safe if the server crashes midway?** Not fully: the two balance updates and the two
  history rows are separate database commits. Production code would wrap them in one DB transaction.
* **Why a token?** So several users can be logged in at once. Tokens are kept in memory, so restarting the
  API logs everyone out.
* **Where is inheritance?** Mainly the Pydantic request classes (`class X(BaseModel)`). If your course
  requires a clearer example, a good addition is a `SavingsAccount(Account)` subclass.
