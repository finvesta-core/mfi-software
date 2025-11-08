import db_functions
import sys
from datetime import date, datetime
import locale

# Set locale for currency formatting (e.g., for '₹' if applicable)
try:
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8') # Example for Indian Rupee/Standard
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C') # Fallback
    except locale.Error:
        pass


# --- ID Conversion Helpers ---

def _format_client_id(client_id: int) -> str:
    """Converts integer client ID to MXXXX format."""
    if client_id is None:
        return "N/A"
    return f"M{client_id:04d}"

def _parse_client_id(client_id_str: str) -> int:
    """Converts MXXXX format string back to integer ID for database queries."""
    client_id_str = client_id_str.strip().upper()
    if client_id_str.startswith('M') and len(client_id_str) > 1:
        try:
            return int(client_id_str[1:])
        except ValueError:
            raise ValueError(f"Invalid member ID format: '{client_id_str}'. Expected MXXXX.")
    try:
        # Allow plain numbers for backwards compatibility/simplicity if no prefix is found
        return int(client_id_str)
    except ValueError:
        raise ValueError(f"Invalid member ID format: '{client_id_str}'. Expected MXXXX.")


def _format_loan_id(loan_id: int) -> str:
    """Converts integer loan ID to PLXXXX format."""
    if loan_id is None:
        return "N/A"
    return f"PL{loan_id:04d}"

def _parse_loan_id(loan_id_str: str) -> int:
    """Converts PLXXXX format string back to integer ID for database queries."""
    loan_id_str = loan_id_str.strip().upper()
    if loan_id_str.startswith('PL') and len(loan_id_str) > 2:
        try:
            return int(loan_id_str[2:])
        except ValueError:
            raise ValueError(f"Invalid loan ID format: '{loan_id_str}'. Numeric part is corrupted.")
    try:
        # Allow plain numbers for simplicity if no prefix is found
        return int(loan_id_str)
    except ValueError:
        raise ValueError(f"Invalid loan ID format: '{loan_id_str}'. Expected PLXXXX.")


# --- Input Helpers ---

def _get_input(prompt: str, type_func=str, min_val=None, max_val=None, parse_id_type=None):
    """Generic input handler with basic validation and optional ID parsing."""
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                if type_func is str and min_val is None and max_val is None:
                    return ""
                raise ValueError("Input cannot be empty.")

            if parse_id_type == 'client':
                return _parse_client_id(value)
            elif parse_id_type == 'loan':
                return _parse_loan_id(value)
            
            # Attempt conversion for standard types
            converted_value = type_func(value)

            # Check range
            if min_val is not None and converted_value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            if max_val is not None and converted_value > max_val:
                print(f"Value cannot exceed {max_val}.")
                continue

            return converted_value
        except ValueError as e:
            if "could not convert string" in str(e):
                print(f"Invalid input type. Please enter a valid {type_func.__name__}.")
            else:
                print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during input: {e}")

def _get_date_input(prompt: str) -> str:
    """Input handler specifically for YYYY-MM-DD dates."""
    while True:
        try:
            date_str = input(prompt).strip()
            datetime.strptime(date_str, "%Y-%m-%d").date() # Validate the format
            return date_str
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD (e.g., 2023-10-25).")

# --- Display Helpers ---

def _format_currency(amount: float) -> str:
    """Formats a float as currency with two decimal places."""
    return f"₹{amount:,.2f}"

def _display_client_details(client_data: dict):
    """Displays formatted client details."""
    print("\n--- Client Details ---")
    print(f"ID: {_format_client_id(client_data['id'])}")
    print(f"Name: {client_data['full_name']}")
    print(f"Contact Info: {client_data['address']}")
    print("-" * 20)

def _display_loan_status(status_data: dict):
    """Displays formatted loan status including monetary values."""
    print("\n--- Loan Status ---")
    print(f"Loan ID: {_format_loan_id(status_data['loan_id'])}")
    print(f"Customer ID: {_format_client_id(status_data['customer_id'])}")
    print(f"Status: {status_data['status']}")
    print(f"Disbursement Date: {status_data['disbursement_date']}")
    print(f"Repayment Frequency: {status_data['repayment_frequency']}")
    print(f"Annual Interest Rate: {status_data['interest_rate']:.2f}%")
    print("-" * 30)
    print(f"Original Principal: {_format_currency(status_data['principal_amount'])}")
    print(f"Total Principal Paid: {_format_currency(status_data['total_principal_paid'])}")
    print(f"Total Interest Paid: {_format_currency(status_data['total_interest_paid'])}")
    print(f"**Remaining Balance**: {_format_currency(status_data['remaining_balance'])}")
    print("-" * 30)


# --- Core Functions ---

def run_register_client():
    """Handles client registration input and output."""
    print("\n--- Register New Client ---")
    full_name = _get_input("Enter full name: ")
    phone_number = _get_input("Enter phone number: ")
    address = _get_input("Enter address: ")
    
    client_id = db_functions.register_client(full_name, phone_number, address)
    if client_id:
        print(f"\n✅ Client Registered Successfully! Client ID: {_format_client_id(client_id)}")
    else:
        print("\n❌ Client registration failed.")

def run_update_client():
    """Handles client update input and output."""
    print("\n--- Update Client Details ---")
    client_id = _get_input("Enter Client ID to update (e.g., M0001): ", type_func=str, parse_id_type='client')
    
    client_data = db_functions.get_client_details(client_id)
    if not client_data:
        print(f"Client ID {_format_client_id(client_id)} not found.")
        return

    _display_client_details(client_data)
    
    new_name = _get_input("Enter new full name (leave blank to keep current): ", type_func=str) or None
    new_phone = _get_input("Enter new phone number (leave blank to keep current): ", type_func=str) or None
    new_address = _get_input("Enter new address (leave blank to keep current): ", type_func=str) or None
    
    if not (new_name or new_phone or new_address):
        print("No updates provided.")
        return
        
    db_functions.update_client_details(client_id, new_name, new_phone, new_address)
    
def run_register_loan():
    """Handles loan registration input, including repayment mode and flat-rate preview."""
    print("\n--- Register New Loan ---")
    client_id = _get_input("Enter Client ID (e.g., M0001): ", type_func=str, parse_id_type='client')
    
    if not db_functions.get_client_details(client_id):
        print(f"Client ID {_format_client_id(client_id)} not found.")
        return

    principal = _get_input("Enter Principal Amount (e.g., 50000): ", type_func=float, min_val=0.01)
    rate = _get_input("Enter Annual Flat Interest Rate (%) (e.g., 10.5): ", type_func=float, min_val=0.0)
    
    term_m = _get_input("Enter Loan Tenure (in full months, e.g., 12): ", type_func=int, min_val=1)
    term_d = _get_input("Enter extra days (0-30): ", type_func=int, min_val=0, max_val=30)
    
    disbursement_date_str = _get_date_input("Enter Disbursement Date (YYYY-MM-DD): ")
    
    freq = _get_input("Enter Repayment Frequency (DAILY/MONTHLY): ", type_func=str).upper()
    while freq not in ['DAILY', 'MONTHLY']:
        print("Invalid frequency. Must be 'DAILY' or 'MONTHLY'.")
        freq = _get_input("Enter Repayment Frequency (DAILY/MONTHLY): ", type_func=str).upper()

    # --- Flat Rate Commitment Preview (using the calculation function) ---
    principal_paise = db_functions._to_int_currency(principal)
    rate_int = db_functions._rate_to_int(rate)
    
    preview = db_functions.calculate_repayment_using_days(principal_paise, rate_int, term_m, term_d)
    
    print("\n--- Loan Commitment Preview (Flat Rate) ---")
    print(f"Total Repayable Amount: {_format_currency(preview['total_repayable_amount'])}")
    print(f"Total Interest Charged: {_format_currency(preview['total_interest'])}")
    print(f"Approx. Monthly Payment: {_format_currency(preview['approx_monthly_payment'])}")
    print("------------------------------------------")

    confirm = _get_input("Confirm loan registration? (yes/no): ", type_func=str).lower()
    if confirm != 'yes':
        print("Loan registration cancelled.")
        return

    loan_id = db_functions.register_loan(client_id, principal, rate, term_m, term_d, disbursement_date_str, freq)
    
    if loan_id:
        print(f"\n✅ Loan Registered Successfully! Loan ID: {_format_loan_id(loan_id)}")
    else:
        print("\n❌ Loan registration failed.")

def run_record_payment():
    """Handles payment input and displays the allocation (Principal vs. Interest)."""
    print("\n--- Record Loan Payment ---")
    # UPDATED: Accept PLXXXX format
    loan_id = _get_input("Enter Loan ID (e.g., PL0001): ", type_func=str, parse_id_type='loan')
    
    status = db_functions.get_loan_status(loan_id)
    if not status:
        print(f"Loan ID {_format_loan_id(loan_id)} not found.")
        return
    if status['status'] == 'CLOSED':
        print(f"Loan ID {_format_loan_id(loan_id)} is already CLOSED.")
        return
        
    payment_date_str = _get_date_input("Enter Payment Date (YYYY-MM-DD): ")
    amount_paid = _get_input("Enter Total Amount Paid (e.g., 1500.00): ", type_func=float, min_val=0.01)
    principal_to_pay = _get_input("Enter Principal amount intended to pay (e.g., 1000.00): ", type_func=float, min_val=0.0)

    result = db_functions.record_payment(loan_id, payment_date_str, amount_paid, principal_to_pay)
    
    if result:
        payment_id, interest_paid, principal_paid = result
        print(f"\n✅ Payment Recorded Successfully! Payment ID: {payment_id}")
        print(f"   Amount Paid: {_format_currency(amount_paid)}")
        print(f"   Allocated to Interest: {_format_currency(interest_paid)}")
        print(f"   Allocated to Principal: {_format_currency(principal_paid)}")
        
        current_status = db_functions.get_loan_status(loan_id)
        if current_status:
            print(f"   **New Remaining Principal Balance**: {_format_currency(current_status['remaining_balance'])}")
    else:
        print("\n❌ Payment recording failed (Check console for error details).")

def run_view_status():
    """Handles viewing the status of a specific loan."""
    # UPDATED: Accept PLXXXX format
    loan_id = _get_input("Enter Loan ID to view status (e.g., PL0001): ", type_func=str, parse_id_type='loan')
    status = db_functions.get_loan_status(loan_id)
    if status and 'error' not in status:
        _display_loan_status(status)
    else:
        print(f"Loan ID {_format_loan_id(loan_id)} not found.")

def run_reports():
    """Handles generating and displaying various reports."""
    while True:
        print("\n--- Reports ---")
        print("1. Active Loan Portfolio Summary")
        print("2. Full Client Summary (All Loans)")
        print("3. Back to Main Menu")
        choice = _get_input("Enter choice (1-3): ", type_func=int, min_val=1, max_val=3)
        
        if choice == 1:
            display_portfolio()
        elif choice == 2:
            display_summary()
        elif choice == 3:
            break

def display_portfolio():
    """Displays a detailed report of all active loans."""
    portfolio = db_functions.get_active_loan_portfolio()
    
    print("\n--- Active Loan Portfolio Summary ---")
    if not portfolio:
        print("No active loans found.")
        return

    print(f"{'Loan ID':<8} | {'Member ID':<10} | {'Client Name':<25} | {'Principal':<12} | {'Paid':<12} | {'Balance':<12} | {'Disbursement Date':<18}")
    print("-" * 105)
    
    total_balance = 0.0
    
    for loan in portfolio:
        member_id_formatted = _format_client_id(loan['client_id'])
        loan_id_formatted = _format_loan_id(loan['loan_id']) # Use formatted ID
        print(
            f"{loan_id_formatted:<8} | {member_id_formatted:<10} | {loan['name']:<25} | "
            f"{_format_currency(loan['principal_amount']):<12} | "
            f"{_format_currency(loan['total_principal_paid']):<12} | "
            f"{_format_currency(loan['remaining_balance']):<12} | "
            f"{loan['disbursement_date']}"
        )
        total_balance += loan['remaining_balance']

    print("-" * 105)
    print(f"{'Total Outstanding Balance:':>72} {_format_currency(total_balance):<12}")
    
def display_summary():
    """Displays a comprehensive report of all clients and their loans."""
    summary = db_functions.get_full_client_summary()
    
    print("\n--- Full Client Summary ---")
    if not summary:
        print("No clients found.")
        return

    for client in summary:
        member_id_formatted = _format_client_id(client['client_id'])
        print(f"\nClient ID: {member_id_formatted} | Name: {client['name']} | Loans: {client['total_loans']}")
        print(f"Contact: {client['contact']}")
        
        if client['loans']:
            print(f"  {'Loan ID':<8} | {'Principal':<12} | {'Paid':<12} | {'Balance':<12} | {'Status':<10}")
            print("  " + "-" * 60)
            for loan in client['loans']:
                loan_id_formatted = _format_loan_id(loan['loan_id']) # Use formatted ID
                print(
                    f"  {loan_id_formatted:<8} | "
                    f"{_format_currency(loan['principal']):<12} | "
                    f"{_format_currency(loan['total_paid']):<12} | "
                    f"{_format_currency(loan['remaining_balance']):<12} | "
                    f"{loan['status']:<10}"
                )
        else:
            print("  (No loans on file)")


def main_menu():
    """Main application loop."""
    db_functions.create_db_tables()
    
    while True:
        print("\n\n--- Microfinance Loan Management System ---")
        print("1. Register New Client")
        print("2. Update Client Details")
        print("3. Register New Loan (Flat Rate)")
        print("4. Record Payment")
        print("5. View Loan Status")
        print("6. Reports")
        print("7. Auto-Close Paid Loans")
        print("8. Exit")
        
        choice = _get_input("Enter choice (1-8): ", type_func=int, min_val=1, max_val=8)

        if choice == 1:
            run_register_client()
        elif choice == 2:
            run_update_client()
        elif choice == 3:
            run_register_loan()
        elif choice == 4:
            run_record_payment()
        elif choice == 5:
            run_view_status()
        elif choice == 6:
            run_reports()
        elif choice == 7:
            count = db_functions.auto_close_paid_loans()
            if count > 0:
                print(f"✅ Successfully closed {count} loans with zero balance.")
            elif count == 0:
                print("No loans were eligible for auto-closure.")
            else:
                print("❌ Auto-closure failed.")
        elif choice == 8:
            print("Exiting application. Goodbye!")
            sys.exit(0)
        
        _get_input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()
