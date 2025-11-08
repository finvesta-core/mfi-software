# reporting_logic.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from database import LoanAccount, AmortizationSchedule, GeneralLedger # Assuming these are correctly imported

def calculate_portfolio_at_risk(db: Session, as_of_date: date = date.today()) -> dict:
    """
    Calculates Portfolio at Risk (PAR) for different overdue buckets (1, 7, 30 days).
    PAR is the total OUTSTANDING PRINCIPAL of all loans with one or more installment overdue 
    by the specified number of days.
    """
    
    # 1. कुल बकाया प्रिंसिपल (Total Outstanding Principal) प्राप्त करें
    # Assuming 'status' is 'ACTIVE' for ongoing loans
    total_principal_outstanding_result = db.query(func.sum(LoanAccount.principal_amount)).filter(
        LoanAccount.status == 'ACTIVE'
    ).scalar() or 0.0

    
    par_buckets = {
        'PAR_1_DAY': 0.0,
        'PAR_7_DAYS': 0.0,
        'PAR_30_DAYS': 0.0
    }
    
    # सक्रिय लोन ID प्राप्त करें
    active_loan_ids = [loan.id for loan in db.query(LoanAccount).filter(LoanAccount.status == 'ACTIVE').all()]
    
    # यदि कोई सक्रिय लोन नहीं है, तो तुरंत रिटर्न करें
    if not active_loan_ids:
        return {
            'total_principal_outstanding': 0.0,
            'PAR_1_DAY': 0.0,
            'PAR_7_DAYS': 0.0,
            'PAR_30_DAYS': 0.0,
        }

    # 2. प्रत्येक PAR बकेट के लिए गणना करें
    for days_overdue, key in [(1, 'PAR_1_DAY'), (7, 'PAR_7_DAYS'), (30, 'PAR_30_DAYS')]:
        
        # ओवरड्यू होने के लिए आवश्यक तिथि सीमा
        # Installment must be due on or before this date:
        overdue_threshold_date = as_of_date - timedelta(days=days_overdue)
        
        # उन सभी लोन IDs को ढूंढें जिनके पास इस सीमा से पहले की कोई UNPAID इंस्टॉलमेंट है
        loans_in_risk = db.query(LoanAccount.id).join(AmortizationSchedule).filter(
            # लोन सक्रिय होना चाहिए
            LoanAccount.id.in_(active_loan_ids),
            # इंस्टॉलमेंट ओवरड्यू सीमा को पार कर चुकी है
            AmortizationSchedule.due_date <= overdue_threshold_date,
            # इंस्टॉलमेंट का भुगतान नहीं हुआ है
            AmortizationSchedule.paid_status == False 
        ).distinct().all()
        
        # ओवरड्यू लोन IDs की लिस्ट निकालें
        risk_loan_ids = [loan[0] for loan in loans_in_risk]
        
        if risk_loan_ids:
            # PAR है उन सभी जोखिम वाले लोनों का कुल बकाया प्रिंसिपल
            par_amount = db.query(func.sum(LoanAccount.principal_amount)).filter(
                LoanAccount.id.in_(risk_loan_ids)
            ).scalar() or 0.0
            
            par_buckets[key] = round(par_amount, 2)
            
        else:
            par_buckets[key] = 0.0

    return {
        'total_principal_outstanding': round(total_principal_outstanding_result, 2),
        'PAR_1_DAY': par_buckets['PAR_1_DAY'],
        'PAR_7_DAYS': par_buckets['PAR_7_DAYS'],
        'PAR_30_DAYS': par_buckets['PAR_30_DAYS'],
    }
    
# Example of another simple report: Collection Efficiency

def calculate_collection_efficiency(db: Session, start_date: date, end_date: date) -> dict:
    """
    Calculates Collection Efficiency for a given date range.
    Efficiency = (Amount Paid) / (Amount Due)
    """
    
    # 1. उस अवधि के लिए कुल देय राशि (Total Due) प्राप्त करें
    total_due_result = db.query(func.sum(AmortizationSchedule.total_emi)).filter(
        AmortizationSchedule.due_date >= start_date,
        AmortizationSchedule.due_date <= end_date
    ).scalar() or 0.0
    
    # 2. उस अवधि में एकत्र की गई कुल राशि (Total Paid) प्राप्त करें
    from database import CollectionTransaction # Ensure this is imported correctly
    total_paid_result = db.query(func.sum(CollectionTransaction.amount_paid)).filter(
        CollectionTransaction.payment_date >= start_date,
        CollectionTransaction.payment_date <= end_date
    ).scalar() or 0.0
    
    
    efficiency = 0.0
    if total_due_result > 0:
        efficiency = (total_paid_result / total_due_result) * 100
        
    return {
        'total_due': round(total_due_result, 2),
        'total_paid': round(total_paid_result, 2),
        'efficiency_percent': round(efficiency, 2)
    }