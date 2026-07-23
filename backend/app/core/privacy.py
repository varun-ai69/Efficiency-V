import base64
from typing import Optional
from cryptography.fernet import Fernet
from app.core.config import settings


def _get_fernet() -> Fernet:
    """Helper to ensure Fernet key is correctly formatted base64."""
    key = settings.FERNET_ENCRYPTION_KEY.encode()
    # If the key provided isn't a valid 32-byte url-safe base64, generate/pad a deterministic base64 key
    try:
        return Fernet(key)
    except Exception:
        # Fallback to generating a valid key derived from key text
        padded = base64.urlsafe_b64encode(key.ljust(32)[:32])
        return Fernet(padded)


def encrypt_sensitive_data(plain_text: Optional[str]) -> Optional[str]:
    """Encrypts a sensitive string (e.g. Full Name, Phone, Medical History) into ciphertext."""
    if plain_text is None:
        return None
    fernet = _get_fernet()
    encrypted_bytes = fernet.encrypt(plain_text.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_sensitive_data(cipher_text: Optional[str]) -> Optional[str]:
    """Decrypts ciphertext back into original sensitive string."""
    if cipher_text is None:
        return None
    try:
        fernet = _get_fernet()
        decrypted_bytes = fernet.decrypt(cipher_text.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception:
        # If decryption fails (e.g. unencrypted plain text fallback), return original text
        return cipher_text
