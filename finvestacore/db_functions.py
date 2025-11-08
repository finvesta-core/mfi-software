import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('microfinance_loans.db')
    cur = conn.cursor()
    
    # Members table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS members (
        id TEXT PRIMARY KEY,
        full_name TEXT,
        father_name TEXT,
        mobile TEXT UNIQUE,
        dob DATE,
        email TEXT,
        gender TEXT,
        occupation TEXT,
        education TEXT,
        address TEXT,
        pincode TEXT,
        district TEXT,
        state TEXT,
        nominee_name TEXT,
        nominee_relation TEXT,
        nominee_age INTEGER,
        account_no TEXT,
        ifsc TEXT,
        bank_name TEXT,
        aadhar TEXT,
        pan TEXT,
        guarantor_name TEXT,
        guarantor_relation TEXT,
        guarantor_mobile TEXT,
        guarantor_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Loans table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        id TEXT PRIMARY KEY,
        member_id TEXT,
        amount REAL,
        interest REAL DEFAULT 30,
        tenure INTEGER,
        repayment_mode TEXT,
        emi_start DATE,
        emi_end DATE,
        total_paid REAL,
        processing_fee REAL,
        mode_of_payment TEXT,
        ref_no TEXT,
        loan_date DATE,
        FOREIGN KEY (member_id) REFERENCES members (id)
    )
    ''')
    
    # Payments table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id TEXT,
        date DATE,
        mode TEXT,
        amount REAL,
        type TEXT,  -- 'EMI' or 'Advance'
        FOREIGN KEY (loan_id) REFERENCES loans (id)
    )
    ''')
    
    # Expenses table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        type TEXT,
        amount REAL,
        description TEXT
    )
    ''')
    
    # Bank balance table (simple)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS bank_balance (
        id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 0,
        cash_in_hand REAL DEFAULT 0
    )
    ''')
    cur.execute('INSERT OR IGNORE INTO bank_balance (id) VALUES (1)')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect('microfinance_loans.db')

def add_member(data):
    conn = get_connection()
    cur = conn.cursor()
    # Generate ID: M0001 etc.
    cur.execute('SELECT COUNT(*) FROM members')
    count = cur.fetchone()[0] + 1
    member_id = f'M{count:04d}'
    data['id'] = member_id
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    cur.execute(f'INSERT INTO members ({columns}) VALUES ({placeholders})', list(data.values()))
    conn.commit()
    conn.close()

def get_members():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM members ORDER BY id DESC')
    members = cur.fetchall()
    conn.close()
    return members

def get_member_by_id(member_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM members WHERE id = ?', (member_id,))
    member = cur.fetchone()
    conn.close()
    return member

# Similar functions for loans, payments, etc.
def add_loan(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM loans')
    count = cur.fetchone()[0] + 1
    loan_id = f'PL{count:04d}'
    data['id'] = loan_id
    # Calculate processing_fee = amount * 0.05
    data['processing_fee'] = data['amount'] * 0.05
    data['total_paid'] = (data['amount'] * 0.05 * 4) + data['amount']  # As per doc
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    cur.execute(f'INSERT INTO loans ({columns}) VALUES ({placeholders})', list(data.values()))
    # Update bank balance if mode is NEFT/IMPS
    if data['mode_of_payment'] in ['IMPS', 'NEFT']:
        update_bank_balance(-data['amount'])
    conn.commit()
    conn.close()

def get_loans_by_member(member_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM loans WHERE member_id = ?', (member_id,))
    loans = cur.fetchall()
    conn.close()
    return loans

def get_due_emi_report(start_date, end_date):
    # Implement query for due EMIs
    conn = get_connection()
    cur = conn.cursor()
    # Complex query based on due dates
    query = '''
    SELECT l.id, m.full_name, m.mobile, m.guarantor_name, l.amount, l.total_paid,
           -- Calculate due EMI, amount, late fee
    FROM loans l JOIN members m ON l.member_id = m.id
    WHERE l.emi_end >= ? AND l.emi_start <= ?
    '''
    cur.execute(query, (start_date, end_date))
    report = cur.fetchall()
    conn.close()
    return report

def get_loan_dispatched_report(start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
    SELECT ROW_NUMBER() OVER (ORDER BY l.id) as sno, l.id, m.full_name, l.amount, l.loan_date, l.emi_end
    FROM loans l JOIN members m ON l.member_id = m.id
    WHERE date(l.loan_date) BETWEEN ? AND ?
    ORDER BY l.loan_date DESC
    ''', (start_date, end_date))
    report = cur.fetchall()
    conn.close()
    return report

def get_bank_balance():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT balance, cash_in_hand FROM bank_balance WHERE id = 1')
    balance = cur.fetchone()
    conn.close()
    return balance

def update_bank_balance(amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('UPDATE bank_balance SET balance = balance + ? WHERE id = 1', (amount,))
    conn.commit()
    conn.close()

def add_expense(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO expenses (date, type, amount, description) VALUES (?, ?, ?, ?)',
                (data['date'], data['type'], data['amount'], data.get('description', '')))
    conn.commit()
    conn.close()

def get_profit_loss():
    # Calculate profit/loss: total loans - total expenses - total interest paid, etc.
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT SUM(amount) FROM loans')
    total_loans = cur.fetchone()[0] or 0
    cur.execute('SELECT SUM(amount) FROM expenses')
    total_expenses = cur.fetchone()[0] or 0
    profit = total_loans - total_expenses  # Simplified
    conn.close()
    return {'profit': profit, 'total_loans': total_loans, 'total_expenses': total_expenses}

# Add more functions as needed, e.g., get_current_loans, get_loan_by_id, etc.