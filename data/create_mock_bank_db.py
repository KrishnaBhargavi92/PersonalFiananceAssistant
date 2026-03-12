import sqlite3
import random
from datetime import datetime, timedelta


class BankTransactionsDB:
    def __init__(self, db_name="bank_transactions.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.seed_mock_data()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT UNIQUE NOT NULL,
                account_holder TEXT NOT NULL,
                account_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                transaction_type TEXT NOT NULL CHECK(transaction_type IN ('credit', 'debit')),
                merchant TEXT,
                reference_id TEXT UNIQUE,
                status TEXT NOT NULL DEFAULT 'completed',
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)

        self.conn.commit()

    def seed_mock_data(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) AS count FROM accounts")
        if cursor.fetchone()["count"] > 0:
            return

        created_at = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO accounts (account_number, account_holder, account_type, created_at)
            VALUES (?, ?, ?, ?)
        """, ("1002003001", "John Smith", "chequing", created_at))

        account_id = cursor.lastrowid

        mock_transactions = [
            ("Payroll Deposit", "Income", 3200.00, "credit", "Employer Inc"),
            ("Apartment Rent", "Housing", 1450.00, "debit", "GreenView Rentals"),
            ("Walmart Purchase", "Groceries", 122.35, "debit", "Walmart"),
            ("Starbucks", "Food", 8.75, "debit", "Starbucks"),
            ("Gas Station", "Transport", 64.20, "debit", "Shell"),
            ("Electric Bill", "Utilities", 96.40, "debit", "Hydro One"),
            ("Internet Bill", "Utilities", 78.99, "debit", "Rogers"),
            ("Freelance Payment", "Income", 550.00, "credit", "Client ABC"),
            ("Restaurant Dinner", "Food", 47.80, "debit", "Boston Pizza"),
            ("ATM Cash Withdrawal", "Cash", 100.00, "debit", "RBC ATM"),
        ]

        base_date = datetime.now() - timedelta(days=10)

        for i, (description, category, amount, transaction_type, merchant) in enumerate(mock_transactions):
            ts = (base_date + timedelta(days=i)).isoformat()
            ref_id = f"TXN{100000+i}"

            cursor.execute("""
                INSERT INTO transactions (
                    account_id, timestamp, description, category, amount,
                    transaction_type, merchant, reference_id, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id,
                ts,
                description,
                category,
                amount,
                transaction_type,
                merchant,
                ref_id,
                "completed"
            ))

        self.conn.commit()

    def get_account_id(self, account_number="1002003001"):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM accounts WHERE account_number = ?", (account_number,))
        row = cursor.fetchone()
        return row["id"] if row else None

    def add_transaction(
        self,
        description,
        category,
        amount,
        transaction_type,
        merchant=None,
        account_number="1002003001",
        status="completed"
    ):
        if amount < 0:
            raise ValueError("Amount must be positive. Use transaction_type='debit' or 'credit'.")

        if transaction_type not in ("credit", "debit"):
            raise ValueError("transaction_type must be 'credit' or 'debit'.")

        account_id = self.get_account_id(account_number)
        if not account_id:
            raise ValueError("Account not found.")

        ts = datetime.now().isoformat()
        ref_id = f"TXN{int(datetime.now().timestamp() * 1000)}"

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (
                account_id, timestamp, description, category, amount,
                transaction_type, merchant, reference_id, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account_id,
            ts,
            description,
            category,
            amount,
            transaction_type,
            merchant,
            ref_id,
            status
        ))

        self.conn.commit()

        return {
            "id": cursor.lastrowid,
            "timestamp": ts,
            "description": description,
            "category": category,
            "amount": amount,
            "transaction_type": transaction_type,
            "merchant": merchant,
            "reference_id": ref_id,
            "status": status
        }

    def get_balance(self, account_number="1002003001"):
        account_id = self.get_account_id(account_number)
        if not account_id:
            return 0.0

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(SUM(
                    CASE
                        WHEN transaction_type = 'credit' THEN amount
                        WHEN transaction_type = 'debit' THEN -amount
                        ELSE 0
                    END
                ), 0) AS balance
            FROM transactions
            WHERE account_id = ?
              AND status = 'completed'
        """, (account_id,))

        return round(cursor.fetchone()["balance"], 2)

    def get_recent_transactions(self, limit=5, account_number="1002003001"):
        account_id = self.get_account_id(account_number)
        if not account_id:
            return []

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                id, timestamp, description, category, amount,
                transaction_type, merchant, reference_id, status
            FROM transactions
            WHERE account_id = ?
            ORDER BY datetime(timestamp) DESC
            LIMIT ?
        """, (account_id, limit))

        return [dict(row) for row in cursor.fetchall()]

    def simulate_real_time_transaction(self, account_number="1002003001"):
        debit_options = [
            ("Tim Hortons", "Food", "Tim Hortons"),
            ("Uber Ride", "Transport", "Uber"),
            ("Metro Groceries", "Groceries", "Metro"),
            ("Amazon Order", "Shopping", "Amazon"),
            ("Pharmacy Purchase", "Health", "Shoppers Drug Mart"),
        ]

        credit_options = [
            ("Refund Processed", "Refund", "Amazon"),
            ("E-transfer Received", "Income", "Interac"),
            ("Cashback Reward", "Reward", "Bank Rewards"),
        ]

        transaction_type = random.choice(["debit", "debit", "debit", "credit"])

        if transaction_type == "debit":
            description, category, merchant = random.choice(debit_options)
            amount = round(random.uniform(5.00, 180.00), 2)
        else:
            description, category, merchant = random.choice(credit_options)
            amount = round(random.uniform(10.00, 250.00), 2)

        return self.add_transaction(
            description=description,
            category=category,
            amount=amount,
            transaction_type=transaction_type,
            merchant=merchant,
            account_number=account_number
        )

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = BankTransactionsDB("bank_transactions.db")

    print("Current Balance:")
    print(db.get_balance())

    print("\nRecent Transactions:")
    for txn in db.get_recent_transactions(10):
        print(txn)

    print("\nAdding one real-time transaction...")
    live_txn = db.simulate_real_time_transaction()
    print(live_txn)

    print("\nUpdated Balance:")
    print(db.get_balance())

    db.close()