from hashlib import md5
from Crypto.Cipher import AES
from base64 import b64decode, b64encode
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class AESCipher:
    def __init__(self, key):
        self.key = md5(key.encode('utf8')).digest()

    # def encrypt(self, data):
    #     iv = get_random_bytes(AES.block_size)
    #     self.cipher = AES.new(self.key, AES.MODE_CBC, iv)
    #     return b64encode(iv + self.cipher.encrypt(pad(data.encode('utf-8'), 
    #         AES.block_size)))
        
    def encrypt(self, message):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ciphered_data = cipher.encrypt(pad(message, AES.block_size))
        iv = cipher.iv
        return [ciphered_data, iv]

    def decrypt(self, ciphered_data, iv):
        cipher = AES.new(self.key, AES.MODE_CBC, iv = iv)
        original = unpad(cipher.decrypt(ciphered_data), AES.block_size)
        return original
    
    # def decrypt(self, data):
    #     raw = b64decode(data)
    #     self.cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
    #     return unpad(self.cipher.decrypt(raw), AES.block_size)
    
# if __name__ == '__main__':
    # print('TESTING ENCRYPTION')
    # msg = input('Message...: ')
    # pwd = input('Password..: ')
    # print('Ciphertext:', AESCipher("pwd").encrypt(msg).decode('utf-8'))

    # print('\nTESTING DECRYPTION')
    # cte = input('Ciphertext: ')
    # pwd = input('Password..: ')
    # print('Message...:', AESCipher(pwd).decrypt(cte).decode('utf-8'))