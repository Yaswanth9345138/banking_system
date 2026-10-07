from account import Account
from decima2l import Decimal
from transactions import (
    deposit,
    withdraw,
    transfer,
    show_transactions,
    show_summary
)


def logged_in_menu(bank):

    while bank.current_user:

        print("\n========== BANKING SYSTEM ==========")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Transfer")
        print("4. Check Balance")
        print("5. Transaction History")
        print("6. Financial Summary")
        print("7. View Profile")
        print("8. Logout")
        print("====================================")

        choice = input("Enter your choice: ").strip()

        account_number = bank.get_account_number()

        if choice == "1":

            try:
                amount = Decimal(input("Enter deposit amount: "))

                deposit(account_number, amount)

            except ValueError:
                print("Please enter a valid amount.")

        elif choice == "2":

            try:
                amount = Decimal(input("Enter withdrawal amount: "))

                withdraw(account_number, amount)

            except ValueError:
                print("Please enter a valid amount.")

        elif choice == "3":

            try:
                receiver = int(
                    input("Enter receiver account number: ")
                )

                amount = Decimal(
                    input("Enter transfer amount: ")
                )

                transfer(
                    account_number,
                    receiver,
                    amount
                )

            except ValueError:
                print("Please enter valid account number and amount.")

        elif choice == "4":

            from database import get_balance

            balance = get_balance(account_number)

            if balance is not None:
                print(f"\nCurrent Balance: ₹{balance:.2f}")

        elif choice == "5":

            show_transactions(account_number)

        elif choice == "6":

            show_summary(account_number)

        elif choice == "7":

            bank.view_profile()

        elif choice == "8":

            bank.logout()

        else:

            print("Invalid choice. Please try again.")


def main():

    bank = Account()

    while True:

        print("\n========== BANKING SYSTEM ==========")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        print("====================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            bank.newuser()

        elif choice == "2":

            if bank.login():

                logged_in_menu(bank)

        elif choice == "3":

            print("Thank you for using the Banking System.")
            break

        else:

            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()