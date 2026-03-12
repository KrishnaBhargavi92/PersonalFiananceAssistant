import sqlite3

def get_db_connection(db_name="./data/bank_transactions.db"):
    conn = sqlite3.connect(db_name, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
