import re
from tools import get_balance, get_recent_transactions

def personalFinanaceAssistant(userInput:str):
    userInput = userInput.lower()
    if "balance" in userInput:
        balance = get_balance()
        return f"Your current balance is ${balance:.2f}."
    if "recent transactions" in userInput:
        transactions = get_recent_transactions()
        if not transactions:
            return "You have no recent transactions."
        response = "Here are your recent transactions:\n"
        for txn in transactions:
            response += f"{txn['timestamp']}: {txn['transaction_type'].capitalize()} of ${txn['amount']:.2f}\n"
        return response
    if "afford" in userInput:
            match = re.search(r"\$?(\d+(?:\.\d{1,2})?)", userInput)
            if match:
                item_price = float(match.group(1))
                balance = get_balance()
                if balance >= item_price:
                    return f"Yes. Your balance is ${balance:.2f}, so you can afford a ${item_price:.2f} purchase."
                else:
                    return f"No. Your balance is ${balance:.2f}, so you cannot afford a ${item_price:.2f} purchase."

    return "Sorry, I didn't understand your request. Please ask about your balance, recent transactions, or if you can afford a purchase."
    