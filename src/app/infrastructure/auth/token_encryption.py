import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from app.config import get_settings

BLOCK_SIZE = 16


def get_aes_key() -> bytes:
    settings = get_settings()
    key = settings.AES_SECRET_KEY.encode("utf-8")
    if len(key) < 32:
        key = key.ljust(32, b"\0")
    return key[:32]


def encrypt_token(token: str) -> str:
    """Encrypt a token using AES-256-CBC."""
    key = get_aes_key()
    cipher = AES.new(key, AES.MODE_CBC)
    padded_data = pad(token.encode("utf-8"), BLOCK_SIZE)
    encrypted = cipher.encrypt(padded_data)
    result = base64.b64encode(bytes(cipher.iv) + encrypted).decode("utf-8")
    return result


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token encrypted with AES-256-CBC."""
    key = get_aes_key()
    data = base64.b64decode(encrypted_token)
    iv = data[:BLOCK_SIZE]
    encrypted = data[BLOCK_SIZE:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted), BLOCK_SIZE)
    return decrypted.decode("utf-8")
