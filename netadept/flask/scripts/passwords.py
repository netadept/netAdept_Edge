from cryptography.fernet import Fernet
import base64
import os

# 1. Generate a key (store this securely; do not regenerate for decryption)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# 2. Encrypt a string
message = "Sensitive Data"
encoded_message = message.encode() # Convert string to bytes
encrypted_message = cipher_suite.encrypt(encoded_message)
print(f"Encrypted: {encrypted_message}")

# 3. Decrypt the string
decrypted_message = cipher_suite.decrypt(encrypted_message)
print(f"Decrypted: {decrypted_message.decode()}")   