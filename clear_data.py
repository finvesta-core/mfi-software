import sqlite3
from datetime import datetime

conn = sqlite3.connect('finvestacore.db')
cur = conn.cursor()

# Clear EMI and advance payments
cur.execute("DELETE FROM payments WHERE type IN ('emi', 'advance')")

# Clear transactions related to payments
cur.execute("DELETE FROM transactions WHERE type IN ('emi', 'advance')")

# Clear loans
cur.execute("DELETE FROM loans")

# Clear investments
cur.execute("DELETE FROM investments")

# Clear expenses
cur.execute("DELETE FROM expenses")

# Clear fees (other income)
cur.execute("DELETE FROM fees")

# Reset loan counter to 0 (new loans from PL0001)
cur.execute("UPDATE counters SET last_id = 0 WHERE name = 'loans'")

conn.commit()
conn.close()

print("All data cleared! New loans will start from PL0001. Investments now force UPI.")