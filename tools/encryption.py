import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESCipher:
    def __init__(self, key):
        self.key = key
    
    def encrypt(self, message):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ciphered_data = cipher.encrypt(pad(message, AES.block_size))
        iv = cipher.iv
        return ciphered_data, iv

    def decrypt(self, ciphered_data, iv):
        if isinstance(iv, str):
            iv = iv.encode()
        if isinstance(ciphered_data, str):
            ciphered_data = ciphered_data.encode() 
        cipher = AES.new(self.key, AES.MODE_CBC, iv = iv)
        original = unpad(cipher.decrypt(ciphered_data), AES.block_size)
        return original

def generate_key(password, salt):
    # Combine the password and salt
    combined = str(password) + str(salt)
    # Use SHA256 to generate a hash
    hash_object = hashlib.sha256(combined.encode())
    # Convert the hash to a hexadecimal string
    hex_dig = hash_object.hexdigest()
    # Convert the hexadecimal string to an integer
    key = int(hex_dig, 16)
    return str(key)[:32]