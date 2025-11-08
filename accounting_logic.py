from sqlalchemy.orm import Session
from database import GeneralLedger, LoanAccount, CollectionTransaction
from datetime import datetime

def post_collection_to_gl(db: Session, loan_tx: CollectionTransaction, 
                          principal_amount: float, interest_amount: float):
    """
    Automates the double-entry posting for a successful collection.
    
    Args:
        db: SQLAlchemy session.
        loan_tx: The newly created CollectionTransaction object.
        principal_amount: The portion of the payment that is Principal.
        interest_amount: The portion of the payment that is Interest.
    """
    
    tx_date = datetime.now()
    
    # ----------------------------------------------------
    # ENTRY 1: DEBIT the Cash Account (Money came IN)
    # DR: Cash A/C
    
    gl_cash_dr = GeneralLedger(
        loan_account_id=loan_tx.loan_account_id,
        transaction_date=tx_date,
        account_head='Cash A/C', 
        debit=loan_tx.amount_paid,
        credit=0.0,
        narration=f"Cash received for Loan ID {loan_tx.loan_account_id} payment."
    )
    db.add(gl_cash_dr)
    db.flush() # Flush to get the ID before committing
    loan_tx.gl_entry_id_1 = gl_cash_dr.id
    
    # ----------------------------------------------------
    # ENTRY 2: CREDIT the Income/Interest & Principal Accounts (Source of money)
    
    # CR: Loan Interest Income A/C
    gl_interest_cr = GeneralLedger(
        loan_account_id=loan_tx.loan_account_id,
        transaction_date=tx_date,
        account_head='Loan Interest Income A/C', 
        debit=0.0,
        credit=interest_amount,
        narration=f"Interest portion of payment for Loan ID {loan_tx.loan_account_id}."
    )
    db.add(gl_interest_cr)

    # CR: Loan Principal Receivable A/C
    gl_principal_cr = GeneralLedger(
        loan_account_id=loan_tx.loan_account_id,
        transaction_date=tx_date,
        account_head='Loan Principal Receivable A/C', 
        debit=0.0,
        credit=principal_amount,
        narration=f"Principal portion of payment for Loan ID {loan_tx.loan_account_id}."
    )
    db.add(gl_principal_cr)
    db.flush()
    
    # Ensure all three entries (one DR, two CR) balance:
    # Debit (Total Paid) = Credit (Interest + Principal)
    
    db.commit()
    return True

# NOTE: You must also create a separate function for the Initial Loan Disbursement GL entry.
# DR: Loan Principal Receivable A/C | CR: Cash/Bank A/C
# accounting_logic.py (Update the file)

from sqlalchemy.orm import Session
from sqlalchemy import func
from database import GeneralLedger, LoanAccount, CollectionTransaction, AmortizationSchedule
from datetime import datetime, date

# ... (post_collection_to_gl function remains the same as previously defined) ...

# -------------------------------------------------------------------------
# NEW LOGIC: Payment Allocation
# -------------------------------------------------------------------------

def get_current_outstanding_principal(db: Session, loan_id: int) -> float:
    """Calculates the current outstanding principal balance for the loan."""
    # This assumes LoanAccount.principal_amount holds the initial principal.
    # We must calculate the total principal paid so far.
    
    # Sum of all 'Principal Paid' recorded in Collection Transactions
    principal_paid_so_far = db.query(
        func.sum(CollectionTransaction.principal_paid)
    ).filter(CollectionTransaction.loan_account_id == loan_id).scalar() or 0.0
    
    initial_principal = db.query(LoanAccount.principal_amount).filter(
        LoanAccount.id == loan_id
    ).scalar() or 0.0
    
    return initial_principal - principal_paid_so_far


def allocate_payment(db: Session, loan_id: int, payment_amount: float, payment_date: date) -> tuple[float, float, float]:
    """
    Allocates the payment amount to Interest and Principal based on the Daily Reducing Balance method.
    
    Returns: (principal_allocated, interest_allocated, remaining_balance)
    """
    loan = db.query(LoanAccount).filter(LoanAccount.id == loan_id).first()
    if not loan:
        raise ValueError("Loan account not found.")

    # 1. Determine the Last Payment/Disbursement Date (to calculate interest period)
    last_tx = db.query(CollectionTransaction).filter(
        CollectionTransaction.loan_account_id == loan_id
    ).order_by(CollectionTransaction.payment_date.desc()).first()
    
    # If no collections yet, use the disbursement date.
    last_date = last_tx.payment_date if last_tx else loan.disbursement_date
    
    # If the last transaction date is the same as the payment date, we skip interest calculation
    if last_date >= payment_date:
        # This payment likely covers a previous period or is a double payment on the same day.
        # For simplicity in this demo, we'll assume a new interest calculation is needed 
        # unless payment_amount is exactly 0.
        pass 
        
    # 2. Get Current Outstanding Principal
    outstanding_principal = get_current_outstanding_principal(db, loan_id)
    
    if outstanding_principal <= 0:
        return 0.0, 0.0, payment_amount # Loan is already fully paid

    # 3. Calculate Interest Due for the period (Daily Reducing Balance)
    
    # Days since last transaction
    days = (payment_date - last_date).days
    
    if days <= 0:
        # If paying on the same day as the last payment, assume only principal is paid
        # unless manual adjustments are needed. For simplicity, we calculate 1 day interest minimum.
        days = 1 
    
    # Daily Interest = (Outstanding Principal * Daily Rate)
    # Annual Rate: loan.interest_rate (e.g., 18%)
    daily_rate = loan.interest_rate / 100 / 365 
    interest_due = outstanding_principal * daily_rate * days
    
    # 4. Allocate Payment
    
    interest_allocated = 0.0
    principal_allocated = 0.0
    remaining_balance = payment_amount
    
    # A. Allocate to Interest First
    if remaining_balance >= interest_due:
        interest_allocated = interest_due
        remaining_balance -= interest_due
    else:
        # If payment is less than interest due, all payment goes to interest.
        interest_allocated = remaining_balance
        remaining_balance = 0.0
        
    # B. Allocate remaining balance to Principal
    if remaining_balance > 0:
        # Do not allow principal allocation to exceed the outstanding principal
        principal_allocation_limit = min(remaining_balance, outstanding_principal)
        principal_allocated = principal_allocation_limit
        remaining_balance -= principal_allocation_limit
        
    return round(principal_allocated, 2), round(interest_allocated, 2), round(remaining_balance, 2)