import base64
import os

from Crypto.Cipher import AES

from app.config import get_settings

NONCE_SIZE = 12  # GCM recommended nonce size
TAG_SIZE = 16  # GCM auth tag size


def get_aes_key() -> bytes:
    settings = get_settings()
    key = settings.AES_SECRET_KEY.encode("utf-8")
    if len(key) < 32:
        key = key.ljust(32, b"\0")
    return key[:32]


def encrypt_token(token: str) -> str:
    """Encrypt a token using AES-256-GCM."""
    key = get_aes_key()
    nonce = os.urandom(NONCE_SIZE)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(token.encode("utf-8"))
    result = base64.b64encode(nonce + tag + ciphertext).decode("utf-8")
    return result


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token encrypted with AES-256-GCM."""
    key = get_aes_key()
    data = base64.b64decode(encrypted_token)
    nonce = data[:NONCE_SIZE]
    tag = data[NONCE_SIZE : NONCE_SIZE + TAG_SIZE]
    ciphertext = data[NONCE_SIZE + TAG_SIZE :]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    decrypted = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted.decode("utf-8")
