import datetime as dt
import math
from sqlalchemy.orm import Session
from database import AmortizationSchedule, LoanAccount # Assuming you've run the database.py update

DAYS_IN_YEAR = 365 # Standard assumption for daily calculation

def calculate_daily_emi(principal: float, annual_rate: float, tenure_days: int) -> float:
    """
    Calculates the fixed Daily Installment using the reducing balance method.
    tenure_days: The total number of days the loan is active (e.g., 365 days for 1 year).
    """
    
    # Daily interest rate (Rate / Days in Year)
    rate_daily = annual_rate / DAYS_IN_YEAR
    
    # Formula check: If rate is zero, handle simple division
    if rate_daily == 0:
        return principal / tenure_days
    
    # Standard EMI formula adapted for daily rate and tenure:
    # EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    # Where: P=Principal, r=Daily Rate, n=Tenure in days
    
    emi = principal * rate_daily * (1 + rate_daily)**tenure_days / ((1 + rate_daily)**tenure_days - 1)
    
    # Rounding to two decimal places is crucial
    return round(emi, 2)

def generate_daily_schedule(db: Session, loan_account: LoanAccount, daily_emi: float):
    """Generates and saves the full daily amortization schedule."""
    
    principal = loan_account.principal_amount
    annual_rate = loan_account.interest_rate_annual
    tenure_months = loan_account.tenure_months # This is still in months from DB, convert it
    disbursement_date = loan_account.disbursement_date
    
    # Assuming one year = 12 months, convert tenure_months to total repayment days (approx)
    # NOTE: You MUST confirm with your business rule if 1 month = 30 days or based on actual calendar days.
    # For now, we assume: Total Days = Tenure Months * (365 / 12)
    # However, for accurate daily calculation, let's use the actual number of days till the end date.
    
    # For simplicity, let's assume the LoanAccount object now stores tenure_days directly.
    # We will use the days provided in the LoanAccount object. For now, let's calculate days:
    total_days = int(tenure_months * (DAYS_IN_YEAR / 12)) 
    
    rate_daily = annual_rate / DAYS_IN_YEAR
    balance = principal
    
    current_due_date = disbursement_date
    
    for i in range(1, total_days + 1):
        # 1. Calculate Interest for the period (Daily): I = P * r
        interest_for_period = balance * rate_daily
        interest_for_period = round(interest_for_period, 2)
        
        # 2. Calculate Principal component: Principal Paid = EMI - Interest
        principal_for_period = daily_emi - interest_for_period
        principal_for_period = round(principal_for_period, 2)
        
        # Handle the last payment adjustment for rounding errors
        if i == total_days:
            principal_for_period = balance # Pay off remaining principal
            total_emi = round(principal_for_period + interest_for_period, 2)
        else:
            total_emi = daily_emi
            
        # 3. Calculate New Balance
        balance -= principal_for_period
        balance = round(balance, 2)
        
        # 4. Calculate next due date (Add one day)
        current_due_date += dt.timedelta(days=1)
        
        # Create and save the schedule entry
        schedule_entry = AmortizationSchedule(
            loan_account_id=loan_account.id,
            installment_number=i,
            due_date=current_due_date,
            principal_due=principal_for_period,
            interest_due=interest_for_period,
            total_emi=total_emi
        )
        db.add(schedule_entry)
        
    db.commit()

# Example usage (for testing)
if __name__ == '__main__':
    P = 20000.0   # Loan Amount
    R = 0.24      # 24% Annual Interest
    D = 365       # 365 Days Tenure (1 year)
    emi = calculate_daily_emi(P, R, D)
    print(f"Calculated Daily EMI for Rs. {P} @ 24% for 365 days: {emi}") 
    # Output should be around 61.16