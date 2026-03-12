from database_connection import get_db_connection

def get_balance():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) as balance FROM transactions WHERE transaction_type = 'credit'")
    credit_sum = cursor.fetchone()["balance"] or 0
    cursor.execute("SELECT SUM(amount) as balance FROM transactions WHERE transaction_type = 'debit'")
    debit_sum = cursor.fetchone()["balance"] or 0
    conn.close()
    return round(credit_sum - debit_sum, 2)

def get_recent_transactions(limit=5):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?", (limit,))
    transactions = cursor.fetchall()
    conn.close()
    return [dict(txn) for txn in transactions]
    
