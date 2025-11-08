import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.ext.declarative import declared_attr
import datetime as dt

# =====================================================================
# 1. DATABASE CONFIGURATION - SWITCHED TO SQLITE
# =====================================================================

# This will create a local file named 'microfinance.db' in your MFI_Software folder.
DATABASE_URL = "sqlite:///./microfinance.db" 

# Note: You can remove the psycopg2-binary package as it's no longer needed.

engine = sa.create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ... (rest of the file remains the same) ...
# =====================================================================
# 2. BASE AND MIXIN (Fix for repeated table definition error)
# =====================================================================

# We use a mixin to ensure tables can be safely redefined (for development/testing)
# and to prevent the 'InvalidRequestError'.
class BaseMixin:
    """Mixin to add __table_args__ and simplify table definitions."""
    @declared_attr
    def __table_args__(cls):
        return {'extend_existing': True}

# We now define models using the BaseMixin
class CustomBase(Base, BaseMixin):
    __abstract__ = True # Prevents SQLAlchemy from creating a table for CustomBase

# =====================================================================
# 3. CONSOLIDATED TABLES (Models)
# =====================================================================

# --- 3.1 Customer Table ---
class Customer(CustomBase):
    __tablename__ = "customers"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    full_name = sa.Column(sa.String, index=True)
    aadhaar_encrypted = sa.Column(sa.String) # Encrypt this data!
    address = sa.Column(sa.String)
    date_joined = sa.Column(sa.DateTime, default=sa.func.now())
    
    # Relationship to get all loans for a customer
    loan_accounts = relationship("LoanAccount", back_populates="customer")

# --- 3.2 Loan Product Table ---
class LoanProduct(CustomBase):
    __tablename__ = "loan_products"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True)
    interest_rate = sa.Column(sa.Float) # Example: 0.12 for 12%
    term_months = sa.Column(sa.Integer) # Max term in months
    # Add more rules here (e.g., processing_fee)

# --- 3.3 Loan Account Table (The Loan Header) ---
class LoanAccount(CustomBase):
    __tablename__ = "loan_accounts"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    
    # Foreign Keys
    customer_id = sa.Column(sa.Integer, sa.ForeignKey('customers.id'), nullable=False)
    # product_id = sa.Column(sa.Integer, sa.ForeignKey('loan_products.id'), nullable=False) # Recommend adding this later
    
    # Loan Terms
    disbursement_date = sa.Column(sa.Date, default=dt.date.today())
    principal_amount = sa.Column(sa.Float, nullable=False)
    annual_interest_rate = sa.Column(sa.Float, nullable=False)
    tenure_months = sa.Column(sa.Integer, nullable=False) # Keep months for primary term
    tenure_days = sa.Column(sa.Integer, default=0) # Extra days for flexibility
    
    status = sa.Column(sa.String, default="Active") # e.g., 'Active', 'Closed', 'Defaulted'
    
    # Relationships
    customer = relationship("Customer", back_populates="loan_accounts")
    schedule = relationship("AmortizationSchedule", back_populates="loan_account")
    transactions = relationship("CollectionTransaction", back_populates="loan_account")

# --- 3.4 Amortization Schedule Table (Expected Repayment Plan) ---
class AmortizationSchedule(CustomBase):
    __tablename__ = "amortization_schedule"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    loan_account_id = sa.Column(sa.Integer, sa.ForeignKey("loan_accounts.id"), nullable=False)
    
    installment_number = sa.Column(sa.Integer, nullable=False)
    due_date = sa.Column(sa.Date, nullable=False)
    
    principal_due = sa.Column(sa.Float, default=0.0)
    interest_due = sa.Column(sa.Float, default=0.0)
    total_emi = sa.Column(sa.Float, default=0.0)
    
    paid_status = sa.Column(sa.Boolean, default=False)
    
    loan_account = relationship("LoanAccount", back_populates="schedule")

# --- 3.5 Collection Transaction Table (Actual Payments) ---
class CollectionTransaction(CustomBase):
    __tablename__ = "collection_transactions"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    loan_account_id = sa.Column(sa.Integer, sa.ForeignKey("loan_accounts.id"), nullable=False)
    
    payment_date = sa.Column(sa.Date, default=sa.func.now())
    amount_paid = sa.Column(sa.Float, nullable=False)
    
    principal_paid = sa.Column(sa.Float, default=0.0)
    interest_paid = sa.Column(sa.Float, default=0.0)
    
    # Link to General Ledger entries for audit trail (Optional but good practice)
    gl_entry_id = sa.Column(sa.Integer, sa.ForeignKey("general_ledger.id"), nullable=True) 
    
    loan_account = relationship("LoanAccount", back_populates="transactions")

# --- 3.6 General Ledger (For Accounting) ---
class GeneralLedger(CustomBase):
    __tablename__ = "general_ledger"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    loan_account_id = sa.Column(sa.Integer, sa.ForeignKey("loan_accounts.id"), nullable=True)
    
    transaction_date = sa.Column(sa.DateTime, default=sa.func.now())
    account_head = sa.Column(sa.String, nullable=False) # e.g., 'Cash A/C', 'Loan Receivable A/C'
    debit = sa.Column(sa.Float, default=0.0)
    credit = sa.Column(sa.Float, default=0.0)
    narration = sa.Column(sa.String)


# =====================================================================
# 4. DATABASE CREATION FUNCTION
# =====================================================================

def create_tables():
    """Function to create all tables defined in Base.metadata."""
    # NOTE: In a real project, use Alembic for safe migrations!
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

# =====================================================================
# 5. EXECUTION BLOCK (Run only when script is executed directly)
# =====================================================================

if __name__ == "__main__":
    create_tables()