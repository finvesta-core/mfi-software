# main_app.py (Add the following imports)
from accounting_logic import post_collection_to_gl
from loan_calc import calculate_daily_emi # To reference the daily EMI
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox, QComboBox

# main_app.py (Update the record_collection method in CollectionEntryWindow)
# ...

def record_collection(self):
        """Handles the collection entry, payment allocation, and GL posting."""
        
        loan_id = self.loan_map.get(self.loan_combo.currentText())
        if not loan_id:
             QMessageBox.critical(self, "Error", "Please select a valid loan account.")
             return
             
        session = SessionLocal()
        try:
            amount_paid = float(self.amount_paid_input.text())
            payment_date_py = dt.date(self.payment_date.date().year(), self.payment_date.date().month(), self.payment_date.date().day())
            
            # --- CRITICAL LOGIC: Payment Allocation (Using the new function) ---
            principal_allocated, interest_allocated, remaining_balance = allocate_payment(
                session, 
                loan_id, 
                amount_paid, 
                payment_date_py
            )

            if principal_allocated + interest_allocated == 0:
                QMessageBox.warning(self, "Warning", "This loan may already be fully paid, or the payment amount is zero.")
                return

            if remaining_balance > 0.01:
                 QMessageBox.information(self, "Partial Payment Note", 
                                        f"₹{remaining_balance:.2f} का शेष भुगतान बच गया है। यह राशि ग्राहक को वापस कर दी जानी चाहिए या अगले भुगतान में एडजस्ट की जानी चाहिए।\n"
                                        f"आवंटित: Principal: ₹{principal_allocated:.2f}, Interest: ₹{interest_allocated:.2f}")

            
            # 1. Save Collection Transaction
            # Note: We only save the actually allocated amount to principal/interest, 
            # not the full amount_paid if there's a small remaining_balance.
            total_allocated = principal_allocated + interest_allocated
            
            new_tx = CollectionTransaction(
                loan_account_id=loan_id,
                amount_paid=total_allocated, # Only log the allocated amount
                payment_date=payment_date_py,
                principal_paid=principal_allocated,
                interest_paid=interest_allocated
            )
            session.add(new_tx)
            session.flush() 

            # 2. Post to General Ledger
            post_collection_to_gl(session, new_tx, principal_allocated, interest_allocated)
            
            # 3. Update Amortization Schedule (Mark installment as paid)
            # Find the first UNPAID installment where the due date is <= payment_date, 
            # and mark it as paid. This is a simplification for daily EMI.
            
            # (Note: For a robust system, this requires checking if the allocated P+I 
            # covers the required EMI amount, but we skip complex schedule tracking here 
            # since the interest calculation is dynamic.)

            # Check if loan is now fully closed
            if get_current_outstanding_principal(session, loan_id) <= 0.01:
                loan_to_close = session.query(LoanAccount).get(loan_id)
                loan_to_close.status = 'CLOSED'
                QMessageBox.information(self, "Success", f"Loan ID {loan_id} has been fully **CLOSED**.")


            session.commit()
            QMessageBox.information(self, "Success", 
                                    f"कलेक्शन ₹{total_allocated:.2f} सफलतापूर्वक दर्ज और पोस्ट किया गया।\n"
                                    f"आवंटन: Principal: ₹{principal_allocated:.2f}, Interest: ₹{interest_allocated:.2f}")
            
            # Clear fields and update display
            self.amount_paid_input.clear()
            self.display_loan_details() 

        except ValueError:
            QMessageBox.critical(self, "Input Error", "कृपया एक मान्य संख्यात्मक राशि दर्ज करें।")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Processing Error", f"लेन-देन या GL पोस्टिंग विफल: {e}")
        finally:
            session.close()

# ... (rest of the CollectionEntryWindow class)
class CollectionEntryWindow(QWidget):
    """Form to record daily collections against a specific loan account."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("दैनिक कलेक्शन दर्ज करें")
        self.setGeometry(150, 150, 800, 600)
        self.layout = QVBoxLayout()
        
        # Loan Selection and Details
        loan_select_layout = QHBoxLayout()
        self.loan_combo = QComboBox()
        self.load_active_loans() # Load active loans into the combobox
        self.loan_combo.currentIndexChanged.connect(self.display_loan_details)
        
        self.details_label = QLabel("लोन विवरण यहां प्रदर्शित होगा।")
        
        loan_select_layout.addWidget(QLabel("लोन अकाउंट चुनें:"))
        loan_select_layout.addWidget(self.loan_combo)
        
        # Payment Inputs
        input_layout = QFormLayout()
        self.amount_paid_input = QLineEdit()
        self.payment_date = QDateEdit(QDate.currentDate())
        
        input_layout.addRow("भुगतान राशि (₹):", self.amount_paid_input)
        input_layout.addRow("भुगतान तिथि:", self.payment_date)
        
        self.collect_btn = QPushButton("कलेक्शन सेव करें और पोस्ट करें")
        self.collect_btn.clicked.connect(self.record_collection)

        # Schedule View (for reference)
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(4)
        self.schedule_table.setHorizontalHeaderLabels(["किस्त सं.", "देय तिथि", "कुल EMI", "भुगतान स्थिति"])

        self.layout.addLayout(loan_select_layout)
        self.layout.addWidget(self.details_label)
        self.layout.addWidget(self.schedule_table)
        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.collect_btn)
        self.setLayout(self.layout)
        
        self.loan_map = {} # Map display text to loan_account_id
        
    # --- Data Loading and Display Functions (TODO) ---
    # This section is the most complex logic (Payment Allocation) and needs to be implemented next.
    
    def load_active_loans(self):
        """Loads active loans into the combobox."""
        session = SessionLocal()
        try:
            active_loans = session.query(LoanAccount).filter(LoanAccount.status == 'ACTIVE').all()
            for loan in active_loans:
                display = f"Loan ID: {loan.id} - Customer: {loan.customer.full_name}"
                self.loan_combo.addItem(display)
                self.loan_map[display] = loan.id
        finally:
            session.close()

    def display_loan_details(self):
        """Displays key loan details and the remaining schedule."""
        # TODO: Implement logic to fetch and display the current balance and schedule for the selected loan
        pass

    def record_collection(self):
        """Handles the collection entry, payment allocation, and GL posting."""
        
        loan_id = self.loan_map.get(self.loan_combo.currentText())
        try:
            amount_paid = float(self.amount_paid_input.text())
            
            # --- CRITICAL LOGIC: Payment Allocation ---
            # 1. Fetch the current loan status and the next due schedule entry.
            # 2. Determine how much of the amount_paid goes to:
            #    a) Interest Due first
            #    b) Principal Due second
            # 3. Update the AmortizationSchedule status (mark installment as paid).
            
            # Placeholder allocation logic (MUST be replaced with complex calc):
            # For simplicity, let's assume the daily EMI is Principal=30, Interest=30, Total=60
            # A full implementation requires fetching the exact Principal/Interest due for the day/period.
            principal_allocated = amount_paid / 2  # Simplified Placeholder
            interest_allocated = amount_paid / 2   # Simplified Placeholder
            
            # 4. Save Collection Transaction
            session = SessionLocal()
            new_tx = CollectionTransaction(
                loan_account_id=loan_id,
                amount_paid=amount_paid,
                principal_paid=principal_allocated,
                interest_paid=interest_allocated
            )
            session.add(new_tx)
            session.flush() # Needed to get new_tx ID before GL posting

            # 5. Post to General Ledger
            post_collection_to_gl(session, new_tx, principal_allocated, interest_allocated)
            
            QMessageBox.information(self, "Success", f"Collection of ₹{amount_paid} recorded for Loan ID {loan_id}.")
            
            # Clear fields and update display
            self.amount_paid_input.clear()
            self.display_loan_details() 

        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter a valid numeric amount.")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Processing Error", f"Failed to record transaction or post to GL: {e}")
        finally:
            session.close()

# --- MainWindow Modification ---
# Add a button in the MainWindow to open the CollectionEntryWindow
class MainWindow(QMainWindow):
    # ... (omitted __init__ for brevity)
    def __init__(self):
        # ... (omitted existing setup)
        
        # New Loan Button
        self.origination_btn = QPushButton("नया लोन वितरित करें")
        self.origination_btn.clicked.connect(self.show_loan_origination)
        main_layout.addWidget(self.origination_btn)

        # Collection Button
        self.collection_btn = QPushButton("दैनिक कलेक्शन दर्ज करें")
        self.collection_btn.clicked.connect(self.show_collection_entry)
        main_layout.addWidget(self.collection_btn)
        
        # Existing Customer Button
        self.add_customer_btn = QPushButton("नया ग्राहक जोड़ें")
        self.add_customer_btn.clicked.connect(self.show_customer_entry)
        main_layout.addWidget(self.add_customer_btn)
        
        # ... (rest of the layout)

    def show_collection_entry(self):
        """Opens the Daily Collection Entry window."""
        self.collection_window = CollectionEntryWindow()
        self.collection_window.show()

# ... (rest of the main_app.py code)
# main_app.py (Modified section)
# Import the utility functions
from encryption_utils import encrypt_data 

class CustomerEntryWindow(QWidget):
    # ... (omitted __init__ for brevity)

    def save_customer_data(self):
        """Fetches input data, encrypts sensitive fields, and saves to the database."""
        name = self.name_input.text()
        aadhaar = self.aadhaar_input.text()
        address = self.address_input.text()
        
        if not name or not aadhaar:
            # Add proper UI error message display here
            print("Error: Name and Aadhaar are mandatory.")
            return

        # --- Apply Encryption Here ---
        encrypted_aadhaar = encrypt_data(aadhaar)
        
        # NOTE: You may also want to encrypt the address if it's considered sensitive PII.
        
        session = SessionLocal()
        try:
            new_customer = Customer(
                full_name=name,
                # Store the encrypted version
                aadhaar_encrypted=encrypted_aadhaar, 
                address=address
            )
            session.add(new_customer)
            session.commit()
            print(f"✅ New Customer Added (Aadhaar Encrypted): {name}")
            # Clear fields and show success message
            self.name_input.clear()
            self.aadhaar_input.clear()
            self.address_input.clear()

        except Exception as e:
            session.rollback()
            print(f"❌ Database Error: {e}")
        finally:
            session.close()

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout
from PyQt6.QtCore import Qt

# Assume database.py and models (Customer, LoanProduct) are correctly set up and accessible
from database import SessionLocal, Customer, create_tables 

class CustomerEntryWindow(QWidget):
    """एक नया ग्राहक जोड़ने के लिए फॉर्म विंडो"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("नया ग्राहक जोड़ें")
        self.setGeometry(200, 200, 400, 300)
        self.layout = QFormLayout()

        # Input Fields
        self.name_input = QLineEdit()
        self.aadhaar_input = QLineEdit()
        self.address_input = QLineEdit()

        self.layout.addRow("पूरा नाम:", self.name_input)
        self.layout.addRow("आधार संख्या (Enc.):", self.aadhaar_input)
        self.layout.addRow("पता:", self.address_input)

        # Save Button
        self.save_button = QPushButton("ग्राहक डेटा सेव करें")
        self.save_button.clicked.connect(self.save_customer_data)
        
        self.layout.addRow(self.save_button)
        self.setLayout(self.layout)

    def save_customer_data(self):
        """इनपुट फ़ील्ड से डेटा लेता है और डेटाबेस में सेव करता है"""
        name = self.name_input.text()
        aadhaar = self.aadhaar_input.text()
        address = self.address_input.text()
        
        if not name or not aadhaar:
            # Add proper error handling UI here
            print("त्रुटि: नाम और आधार अनिवार्य हैं।")
            return

        session = SessionLocal()
        try:
            # NOTE: यहां Aadhaar encryption logic जोड़ी जाएगी। अभी यह RAW सेव कर रहा है।
            new_customer = Customer(
                full_name=name,
                aadhaar_encrypted=aadhaar, 
                address=address
            )
            session.add(new_customer)
            session.commit()
            print(f"✅ नया ग्राहक जोड़ा गया: {name}")
            # Clear fields after successful save
            self.name_input.clear()
            self.aadhaar_input.clear()
            self.address_input.clear()

        except Exception as e:
            session.rollback()
            print(f"❌ डेटाबेस एरर: {e}")
        finally:
            session.close()


class MainWindow(QMainWindow):
    """एप्लीकेशन की मुख्य विंडो, जहां से अन्य फंक्शन एक्सेस होंगे"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("माइक्रोफाइनेंस LMS - मुख्य डैशबोर्ड")
        self.setGeometry(100, 100, 800, 600)
        
        # Central Widget and Layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Add Customer Button
        self.add_customer_btn = QPushButton("नया ग्राहक जोड़ें")
        self.add_customer_btn.clicked.connect(self.show_customer_entry)
        main_layout.addWidget(self.add_customer_btn)

        # Placeholder for future widgets (Data Table, MIS)
        main_layout.addWidget(QLabel("यहां ग्राहक सूची और MIS डैशबोर्ड आएगा..."))

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def show_customer_entry(self):
        """नया ग्राहक जोड़ने के लिए विंडो खोलता है"""
        self.customer_window = CustomerEntryWindow()
        self.customer_window.show()


if __name__ == "__main__":
    # Ensure tables exist before running the app
    # Run create_tables() only once when setting up the database initially!
    # create_tables() 
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    # main_app.py (Add the following imports)
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from encryption_utils import decrypt_data 
# ... (existing imports)

class CustomerListView(QWidget):
    """Displays a list of all customers from the PostgreSQL database."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("सभी ग्राहक सूची")
        self.layout = QVBoxLayout()
        
        # 1. Table Widget Setup
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels([
            "ID", "पूरा नाम", "आधार (Encrypted)", "पता"
        ])
        
        # 2. Add Decrypt Button
        self.decrypt_button = QPushButton("चयनित आधार संख्या देखें (Decrypt)")
        self.decrypt_button.clicked.connect(self.decrypt_selected_aadhaar)
        
        self.layout.addWidget(self.customer_table)
        self.layout.addWidget(self.decrypt_button)
        self.setLayout(self.layout)
        
        # Load data immediately
        self.load_customer_data()

    def load_customer_data(self):
        """Fetches all customer data (including encrypted Aadhaar) from the database."""
        session = SessionLocal()
        try:
            customers = session.query(Customer).all()
            
            self.customer_table.setRowCount(len(customers))
            
            for row_num, customer in enumerate(customers):
                # ID and Name are stored as normal text
                self.customer_table.setItem(row_num, 0, QTableWidgetItem(str(customer.id)))
                self.customer_table.setItem(row_num, 1, QTableWidgetItem(customer.full_name))
                
                # Encrypted Aadhaar is shown by default
                # We use a placeholder to indicate it's encrypted
                encrypted_text = customer.aadhaar_encrypted[:5] + "..." 
                self.customer_table.setItem(row_num, 2, QTableWidgetItem(encrypted_text))
                
                self.customer_table.setItem(row_num, 3, QTableWidgetItem(customer.address))

        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"डेटा लोड करने में त्रुटि: {e}")
        finally:
            session.close()

    def decrypt_selected_aadhaar(self):
        """Decrypts and shows the Aadhaar of the selected row."""
        selected_rows = self.customer_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "चयन त्रुटि", "कृपया पहले ग्राहक की एक पंक्ति चुनें।")
            return

        # Get the ID of the selected customer (Column 0)
        selected_row_index = selected_rows[0].row()
        customer_id = int(self.customer_table.item(selected_row_index, 0).text())
        
        session = SessionLocal()
        try:
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                # Retrieve the full encrypted string from the database object
                encrypted_aadhaar = customer.aadhaar_encrypted
                
                # --- Decrypt the Data ---
                decrypted_aadhaar = decrypt_data(encrypted_aadhaar)
                
                # Show the result in a dialog box
                QMessageBox.information(
                    self, 
                    "आधार विवरण", 
                    f"ग्राहक: {customer.full_name}\nडिक्रिप्टेड आधार संख्या: {decrypted_aadhaar}"
                )
            
        except Exception as e:
            QMessageBox.critical(self, "डिक्रिप्शन त्रुटि", f"डेटा डिक्रिप्ट करते समय त्रुटि: {e}")
        finally:
            session.close()

# --- MainWindow Modification ---
# Modify the MainWindow class in main_app.py to include the new list view.
class MainWindow(QMainWindow):
    # ... (omitted __init__ for brevity)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("माइक्रोफाइनेंस LMS - मुख्य डैशबोर्ड")
        self.setGeometry(100, 100, 1000, 700) # Made window larger
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Buttons
        self.add_customer_btn = QPushButton("नया ग्राहक जोड़ें")
        self.add_customer_btn.clicked.connect(self.show_customer_entry)
        main_layout.addWidget(self.add_customer_btn)
        
        # Display the Customer List View
        self.customer_list = CustomerListView()
        main_layout.addWidget(self.customer_list)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    # ... (omitted show_customer_entry for brevity)


if __name__ == "__main__":
    # Ensure tables exist (Run this only once when initializing the DB!)
    # create_tables() 
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    # main_app.py (Add the following imports)
from PyQt6.QtWidgets import QComboBox, QDateEdit 
from PyQt6.QtCore import QDate 
import datetime as dt

# Import all required models and functions
from database import SessionLocal, Customer, LoanProduct, LoanAccount, create_tables 
from loan_calc import calculate_daily_emi, generate_daily_schedule 

class LoanOriginationWindow(QWidget):
    """Form to sanction a new loan, calculate EMI, and generate the schedule."""
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("नया लोन वितरित करें (Daily Repayment)")
        self.setGeometry(150, 150, 600, 500)
        self.main_window = main_window # Reference to the main window for updates
        self.layout = QFormLayout()

        # --- Data Fetching (Dropdowns) ---
        self.customer_combo = QComboBox()
        self.product_combo = QComboBox()
        
        # Internal dictionaries to map names to database IDs
        self.customer_map = self.load_customers()
        self.product_map = self.load_products()

        # --- Input Fields ---
        self.principal_input = QLineEdit()
        self.tenure_input = QLineEdit() # Input in Days
        self.disbursement_date = QDateEdit(QDate.currentDate())
        
        # --- Output Fields (Read-Only) ---
        self.rate_label = QLabel("वार्षिक दर (A.R.): 0.0%")
        self.emi_output = QLabel("दैनिक EMI: ₹ 0.00")
        
        # --- Buttons ---
        self.calculate_btn = QPushButton("EMI गणना करें")
        self.calculate_btn.clicked.connect(self.calculate_emi_action)
        
        self.disburse_btn = QPushButton("लोन वितरित करें और अनुसूची सेव करें")
        self.disburse_btn.setEnabled(False) # Disabled until EMI is calculated
        self.disburse_btn.clicked.connect(self.disburse_loan_action)

        # --- Form Layout Setup ---
        self.layout.addRow("ग्राहक चुनें:", self.customer_combo)
        self.layout.addRow("लोन उत्पाद चुनें:", self.product_combo)
        self.layout.addRow(self.rate_label)
        self.layout.addRow(QLabel("मूलधन राशि (₹):"), self.principal_input)
        self.layout.addRow(QLabel("अवधि (दिनों में):"), self.tenure_input)
        self.layout.addRow(QLabel("वितरण तिथि:"), self.disbursement_date)
        self.layout.addRow(self.calculate_btn)
        self.layout.addRow(self.emi_output)
        self.layout.addRow(self.disburse_btn)
        
        self.setLayout(self.layout)
        
        # Connect product change to update rate label
        self.product_combo.currentIndexChanged.connect(self.update_rate_label)
        self.update_rate_label() # Initial call

    def load_customers(self):
        """Fetches customers from DB and fills the dropdown."""
        session = SessionLocal()
        customer_map = {}
        try:
            customers = session.query(Customer).all()
            for customer in customers:
                display_name = f"{customer.full_name} (ID: {customer.id})"
                self.customer_combo.addItem(display_name)
                customer_map[display_name] = customer.id
        finally:
            session.close()
        return customer_map

    def load_products(self):
        """Fetches loan products from DB and fills the dropdown."""
        session = SessionLocal()
        product_map = {}
        try:
            products = session.query(LoanProduct).all()
            for product in products:
                display_name = f"{product.name} ({product.interest_rate*100:.2f}%)"
                self.product_combo.addItem(display_name)
                product_map[product.name] = (product.id, product.interest_rate) # Store ID and Rate
        finally:
            session.close()
        return product_map

    def update_rate_label(self):
        """Updates the rate label based on the selected product."""
        selected_text = self.product_combo.currentText()
        if not selected_text:
            self.rate_label.setText("वार्षिक दर (A.R.): 0.0%")
            return
            
        # Extract product name from the displayed text
        product_name = selected_text.split(' (')[0]
        
        # Lookup the rate
        _, rate = self.product_map.get(product_name, (None, 0.0))
        self.rate_label.setText(f"वार्षिक दर (A.R.): {rate*100:.2f}%")
        
    def calculate_emi_action(self):
        """Handles EMI calculation and updates the output field."""
        try:
            principal = float(self.principal_input.text())
            tenure_days = int(self.tenure_input.text())
            
            selected_text = self.product_combo.currentText()
            product_name = selected_text.split(' (')[0]
            _, annual_rate = self.product_map.get(product_name)
            
            if principal <= 0 or tenure_days <= 0 or annual_rate is None:
                raise ValueError("मान्य इनपुट दर्ज करें।")

            # Calculate Daily EMI
            self.calculated_emi = calculate_daily_emi(principal, annual_rate, tenure_days)
            
            self.emi_output.setText(f"दैनिक EMI: ₹ {self.calculated_emi:.2f}")
            self.disburse_btn.setEnabled(True) # Enable save button after calculation

        except ValueError as e:
            QMessageBox.critical(self, "इनपुट त्रुटि", f"कृपया सही संख्यात्मक मान दर्ज करें।\nत्रुटि: {e}")
            self.disburse_btn.setEnabled(False)
        except Exception as e:
             QMessageBox.critical(self, "त्रुटि", f"गणना में अज्ञात त्रुटि: {e}")
             self.disburse_btn.setEnabled(False)

    def disburse_loan_action(self):
        """Saves LoanAccount and generates Amortization Schedule."""
        try:
            # 1. Retrieve final data
            customer_display = self.customer_combo.currentText()
            customer_id = self.customer_map.get(customer_display)
            
            product_display = self.product_combo.currentText()
            product_name = product_display.split(' (')[0]
            product_id, annual_rate = self.product_map.get(product_name)
            
            principal = float(self.principal_input.text())
            tenure_days = int(self.tenure_input.text())
            
            # Convert QDate to Python date object
            qdate = self.disbursement_date.date()
            disbursement_date = dt.date(qdate.year(), qdate.month(), qdate.day())
            
            if not customer_id or not product_id:
                 raise ValueError("ग्राहक या उत्पाद मान्य नहीं है।")

            # 2. Save LoanAccount to DB
            session = SessionLocal()
            new_loan = LoanAccount(
                customer_id=customer_id,
                product_id=product_id,
                principal_amount=principal,
                interest_rate_annual=annual_rate,
                tenure_days=tenure_days,
                disbursement_date=disbursement_date
            )
            session.add(new_loan)
            session.commit() # Commit to get the loan_account ID
            
            # 3. Generate Schedule using the saved loan object
            generate_daily_schedule(session, new_loan, self.calculated_emi)
            
            QMessageBox.information(self, "सफलता", f"लोन ID {new_loan.id} सफलतापूर्वक वितरित और शेड्यूल किया गया।")
            
            # Close the window
            self.close()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "वितरण त्रुटि", f"लोन वितरित करते समय त्रुटि: {e}")
        finally:
            session.close()

# --- MainWindow Modification ---
# Add a button in the MainWindow to open the LoanOriginationWindow
class MainWindow(QMainWindow):
    # ... (omitted __init__ for brevity)
    def __init__(self):
        super().__init__()
        # ... (omitted existing setup)
        
        # New Loan Button
        self.origination_btn = QPushButton("नया लोन वितरित करें")
        self.origination_btn.clicked.connect(self.show_loan_origination)
        main_layout.addWidget(self.origination_btn)

        # Existing Customer Button
        self.add_customer_btn = QPushButton("नया ग्राहक जोड़ें")
        self.add_customer_btn.clicked.connect(self.show_customer_entry)
        main_layout.addWidget(self.add_customer_btn)
        
        # ... (rest of the layout)

    def show_loan_origination(self):
        """Opens the Loan Origination window."""
        self.loan_window = LoanOriginationWindow(self)
        self.loan_window.show()
        # main_app.py (Add new imports at the top)
from reporting_logic import calculate_portfolio_at_risk, calculate_collection_efficiency
from PyQt6.QtCore import QDate

class ReportingWindow(QWidget):
    """Displays key MIS reports like PAR and Collection Efficiency."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIS रिपोर्टिंग और पोर्टफोलियो सारांश")
        self.setGeometry(150, 150, 700, 500)
        self.layout = QVBoxLayout()
        
        # --- PAR Section ---
        self.par_title = QLabel("<h2>पोर्टफोलियो एट रिस्क (PAR)</h2>")
        self.par_results = QTableWidget()
        self.par_results.setRowCount(4)
        self.par_results.setColumnCount(2)
        self.par_results.setHorizontalHeaderLabels(["PAR बकेट", "बकाया प्रिंसिपल राशि (₹)"])
        self.par_results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.load_par_data()
        
        # --- Collection Efficiency Section ---
        self.ce_title = QLabel("<h2>कलेक्शन एफ़िशिएंसी</h2>")
        
        # Date Pickers for CE range
        self.ce_start_date = QDateEdit(QDate.currentDate().addDays(-30)) # Last 30 days default
        self.ce_end_date = QDateEdit(QDate.currentDate())
        self.ce_calc_btn = QPushButton("एफ़िशिएंसी गणना करें")
        self.ce_calc_btn.clicked.connect(self.load_collection_efficiency)
        
        ce_date_layout = QHBoxLayout()
        ce_date_layout.addWidget(QLabel("आरंभ तिथि:"))
        ce_date_layout.addWidget(self.ce_start_date)
        ce_date_layout.addWidget(QLabel("समाप्ति तिथि:"))
        ce_date_layout.addWidget(self.ce_end_date)
        ce_date_layout.addWidget(self.ce_calc_btn)
        
        self.ce_output = QLabel("परिणाम: **0.00%** (₹0.00 Paid / ₹0.00 Due)")
        
        # --- Final Layout Assembly ---
        self.layout.addWidget(self.par_title)
        self.layout.addWidget(self.par_results)
        self.layout.addWidget(self.ce_title)
        self.layout.addLayout(ce_date_layout)
        self.layout.addWidget(self.ce_output)
        self.setLayout(self.layout)
        
        self.load_collection_efficiency() # Initial load

    def load_par_data(self):
        """Fetches and displays PAR data."""
        session = SessionLocal()
        try:
            par_data = calculate_portfolio_at_risk(session)
            
            data = [
                ("कुल बकाया प्रिंसिपल", par_data['total_principal_outstanding']),
                ("PAR > 1 दिन", par_data['PAR_1_DAY']),
                ("PAR > 7 दिन", par_data['PAR_7_DAYS']),
                ("PAR > 30 दिन (गंभीर)", par_data['PAR_30_DAYS'])
            ]
            
            self.par_results.setRowCount(len(data))
            for i, (label, amount) in enumerate(data):
                self.par_results.setItem(i, 0, QTableWidgetItem(label))
                self.par_results.setItem(i, 1, QTableWidgetItem(f"₹ {amount:,.2f}"))
                
            self.par_results.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "त्रुटि", f"PAR डेटा लोड करने में विफल: {e}")
        finally:
            session.close()

    def load_collection_efficiency(self):
        """Fetches and displays Collection Efficiency."""
        session = SessionLocal()
        try:
            start_date_py = dt.date(self.ce_start_date.date().year(), self.ce_start_date.date().month(), self.ce_start_date.date().day())
            end_date_py = dt.date(self.ce_end_date.date().year(), self.ce_end_date.date().month(), self.ce_end_date.date().day())

            if start_date_py > end_date_py:
                QMessageBox.warning(self, "तिथि त्रुटि", "आरंभ तिथि, समाप्ति तिथि से पहले होनी चाहिए।")
                return

            ce_data = calculate_collection_efficiency(session, start_date_py, end_date_py)
            
            output_text = (
                f"परिणाम: **{ce_data['efficiency_percent']:.2f}%** "
                f"(₹{ce_data['total_paid']:,.2f} Paid / ₹{ce_data['total_due']:,.2f} Due)"
            )
            self.ce_output.setText(output_text)

        except Exception as e:
            QMessageBox.critical(self, "त्रुटि", f"कलेक्शन एफ़िशिएंसी गणना में विफल: {e}")
        finally:
            session.close()

# --- MainWindow Modification ---
class MainWindow(QMainWindow):
    # ... (omitted __init__ for brevity)
    def __init__(self):
        # ... (omitted existing setup)
        
        # New Report Button
        self.report_btn = QPushButton("MIS रिपोर्ट देखें")
        self.report_btn.clicked.connect(self.show_reports)
        main_layout.addWidget(self.report_btn)

        # Existing Buttons...
        # ...

    def show_reports(self):
        """Opens the MIS Reporting window."""
        self.report_window = ReportingWindow()
        self.report_window.show()