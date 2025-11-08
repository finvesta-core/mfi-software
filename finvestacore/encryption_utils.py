from cryptography.fernet import Fernet
import os

# --- CRITICAL: THE ENCRYPTION KEY ---
# इस कुंजी को एक बार जनरेट करें और इसे कहीं सुरक्षित जगह पर स्टोर करें।
# यदि यह कुंजी खो गई, तो आप अपना सारा एन्क्रिप्टेड डेटा हमेशा के लिए खो देंगे।
# You MUST treat this key like the most valuable secret.
# Example: 
# ENCRYPTION_KEY = b'45u892pB1w... (Your unique key)' 
# For demonstration, we'll use a placeholder/dummy logic. You must generate and save yours securely.

# Generate a key (Run this once on a separate script to get your key)
# key = Fernet.generate_key() 
# print(key) # Copy this outputted key and use it below.

# Placeholder Key (REPLACE THIS WITH YOUR SECURE GENERATED KEY!)
ENCRYPTION_KEY = b'vUaF-6sT-s9Q0I3D_wXyZ-aBcD-eFgH-iJkL-mNoP-qRsT-uVwX-yZaB-cD' 
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """Encrypts a string (like Aadhaar) using Fernet."""
    if not data:
        return ""
    # Data must be encoded to bytes before encryption
    encrypted_bytes = fernet.encrypt(data.encode())
    # Return the encrypted bytes as a string for storage in PostgreSQL
    return encrypted_bytes.decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts a string back to its original form."""
    if not encrypted_data:
        return ""
    try:
        # Data must be re-encoded to bytes before decryption
        decrypted_bytes = fernet.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()
    except Exception as e:
        # Handle errors like invalid key or corrupted data
        print(f"Decryption Error: {e}")
        return "DECRYPTION_FAILED"

if __name__ == '__main__':
    test_data = "123456789012"
    encrypted = encrypt_data(test_data)
    decrypted = decrypt_data(encrypted)
    
    print(f"Original: {test_data}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")