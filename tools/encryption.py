import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def aes_encode(key: bytes, message: str) -> str:
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    ct = base64.b64encode(cipher.iv + ct_bytes).decode()
    return ct

def aes_decode(key: bytes, ct: str) -> str:
    ct = base64.b64decode(ct)
    iv = ct[:16]
    ct = ct[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
    return pt