from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import datetime as dt

# Import Database and Models (assuming they are set up correctly)
from database import SessionLocal, LoanAccount, AmortizationSchedule, CollectionTransaction
from accounting_logic import post_collection_to_gl # Required for collection posting

app = FastAPI(
    title="MFI Local Sync API", 
    description="Secure local API for syncing collections with the desktop LMS."
)

# Pydantic Schemas for Data Transfer (What mobile sends/receives)

class ScheduleItem(BaseModel):
    """Schema for a single schedule item to be sent to mobile."""
    loan_id: int
    installment_number: int
    due_date: dt.date
    total_emi: float
    paid_status: bool
    
class CollectionIn(BaseModel):
    """Schema for a single collection entry received from mobile."""
    loan_id: int
    amount_paid: float
    payment_date: dt.date
    # Optional: collector_id, collection_center
    
# --- 1. DOWNLOAD Endpoint (Pushing Schedules to Mobile) ---
@app.get("/sync/loan_schedules", response_model=List[ScheduleItem])
def get_active_schedules():
    """Fetches all UNPAID schedule items for active loans."""
    session = SessionLocal()
    try:
        # Fetch only the schedule items that are NOT paid yet
        schedules = session.query(AmortizationSchedule).join(LoanAccount).filter(
            LoanAccount.status == 'ACTIVE',
            AmortizationSchedule.paid_status == False
        ).all()
        
        # Format the data according to the Pydantic schema
        data_to_sync = []
        for item in schedules:
            data_to_sync.append(ScheduleItem(
                loan_id=item.loan_account_id,
                installment_number=item.installment_number,
                due_date=item.due_date,
                total_emi=item.total_emi,
                paid_status=item.paid_status
            ))
        
        return data_to_sync
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error during sync: {e}")
    finally:
        session.close()

# --- 2. UPLOAD Endpoint (Pulling Collections from Mobile) ---
@app.post("/sync/collections")
def receive_collections(collections: List[CollectionIn]):
    """Receives a list of collection transactions and posts them to the GL."""
    session = SessionLocal()
    transactions_processed = 0
    
    try:
        for collection in collections:
            # 1. Fetch Loan Details
            loan = session.query(LoanAccount).filter(LoanAccount.id == collection.loan_id).first()
            if not loan:
                print(f"Loan ID {collection.loan_id} not found. Skipping transaction.")
                continue

            # 2. CRITICAL: Payment Allocation Logic (Needs full implementation)
            # This is where you allocate: Amount Paid -> Interest Paid -> Principal Paid
            # For this demo, we will use a simple allocation (e.g., 50/50 split)
            
            principal_allocated = round(collection.amount_paid / 2, 2) 
            interest_allocated = round(collection.amount_paid / 2, 2)
            
            # 3. Create Collection Transaction
            new_tx = CollectionTransaction(
                loan_account_id=collection.loan_id,
                amount_paid=collection.amount_paid,
                payment_date=collection.payment_date,
                principal_paid=principal_allocated,
                interest_paid=interest_allocated
            )
            session.add(new_tx)
            session.flush() # Get TX ID
            
            # 4. Post to General Ledger (Automatic Double-Entry)
            post_collection_to_gl(session, new_tx, principal_allocated, interest_allocated)
            
            # 5. Update Amortization Schedule (Mark nearest installment as paid)
            # Find the closest unpaid installment to the payment_date and mark it True
            
            # Placeholder for schedule update:
            # schedule_item = session.query(AmortizationSchedule).filter(...).first()
            # if schedule_item:
            #     schedule_item.paid_status = True
            
            transactions_processed += 1

        session.commit()
        return {"status": "success", "message": f"{transactions_processed} transactions processed and posted to GL."}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction processing failed: {e}")
    finally:
        session.close()