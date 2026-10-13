# Banking System

A banking system written in Python (OOP, file I/O, MySQL) with a Flutter front end.

```
Flutter app (bank_app/)  --HTTP/JSON-->  api.py  -->  account.py + transactions.py  -->  database.py  -->  MySQL
Console menu (main.py)  ------------------------------^   (same logic, no web layer)
```

## Features

* Register / log in (SHA-256 password hashing, email + password validation)
* Automatic account numbers starting at 1000
* Deposit, withdraw, transfer between accounts
* Balance, transaction history, financial summary, profile
* Statement export to a `.txt` file
* Two interfaces on the same code: console menu and Flutter app

## Files

| File | Job |
| --- | --- |
| `account.py` | `Account` class: registration, login, profile; creates the database and tables |
| `database.py` | All MySQL queries (balance, transactions, account lookup); holds the DB login |
| `transactions.py` | Deposit, withdraw, transfer, history and summary rules |
| `main.py` | Console menu |
| `api.py` | FastAPI web API used by the Flutter app |
| `bank_app/` | Flutter front end |
| `datatbase.sql` | Optional manual schema (Python also creates the tables itself) |
| `docs/CODE_WALKTHROUGH.md` | Explanation of every part + demo script |

## 1. Set up the Python side

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create the MySQL user once:

```sql
CREATE USER IF NOT EXISTS 'bankuser'@'localhost' IDENTIFIED BY 'bankpassword123';
GRANT ALL PRIVILEGES ON *.* TO 'bankuser'@'localhost';
FLUSH PRIVILEGES;
```

The login lives in `DB_CONFIG` in `database.py` (or set the `BANK_DB_HOST`, `BANK_DB_USER`,
`BANK_DB_PASSWORD` environment variables). The database and both tables are created automatically.

### Run the console version

```bash
python main.py
```

### Run the API (needed for the Flutter app)

```bash
uvicorn api:app --reload
```

Check it at <http://127.0.0.1:8000/docs> (interactive page listing every endpoint).

## 2. Run the Flutter app

Needs the [Flutter SDK](https://docs.flutter.dev/get-started/install). Keep the API running, then:

```bash
cd bank_app
flutter create .          # one-time: generates android/, web/, windows/ ... (keeps our lib/ and pubspec.yaml)
flutter pub get
flutter run -d chrome     # or: -d windows / -d linux / -d macos
```

* **Chrome / desktop:** works with no extra setup.
* **Android emulator:** the app already uses `10.0.2.2` to reach your computer. Android blocks plain
  `http://` by default, so add `android:usesCleartextTraffic="true"` to the `<application>` tag in
  `bank_app/android/app/src/main/AndroidManifest.xml`.
* **Real phone:** start the API with `uvicorn api:app --host 0.0.0.0`, then on the login screen tap
  *Server address* and enter `http://<your-computer-IP>:8000` (same Wi-Fi).

Run the Flutter unit tests with `flutter test`.

## API endpoints

| Method | Path | Needs login | Purpose |
| --- | --- | --- | --- |
| POST | `/register` | no | Create account |
| POST | `/login` | no | Returns a token |
| POST | `/logout` | yes | End the session |
| GET | `/profile`, `/balance`, `/transactions`, `/summary` | yes | Read account data |
| POST | `/deposit`, `/withdraw`, `/transfer` | yes | Move money |
| GET | `/export` | yes | Statement as a `.txt` file |

Logged-in requests send `Authorization: Bearer <token>`.

> **Note:** academic project. A production bank would need salted password hashing (bcrypt/argon2),
> database transactions around every money movement, HTTPS, token expiry and rate limiting.
