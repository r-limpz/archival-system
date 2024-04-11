from argon2 import PasswordHasher
import binascii

# Initialize the PasswordHasher object
ph = PasswordHasher()

# The plaintext password to be hashed
password = "admin"

# Hash the password
hash = ph.hash(password)

# Convert the hash to hexadecimal form
hex_hash = binascii.hexlify(hash.encode()).decode()
original_hash = binascii.unhexlify(hex_hash).decode()

# Verify the password
try:
    ph.verify(hash, password)
    verifier = True
except:
    verifier = False

# Print the results
print("Encoded form:", hash)
print("Hex form:", hex_hash)
print("deHex   form:", original_hash)
print("Verifier is:", verifier)
