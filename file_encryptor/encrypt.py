# import required module
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_key() -> bytes:
    encryption_key = Fernet.generate_key()
    return encryption_key


def generate_key_password(password: bytes) -> tuple:
    """
    :param password: password as a bytestring to generate key
    :return: Encryption key, salt
    """
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    encryption_key = base64.urlsafe_b64encode(kdf.derive(password))
    return encryption_key, salt


def generate_key_from_salt(password: bytes, salt: bytes) -> bytes:
    """
        :param salt: 16 byte salt passed as argument
        :param password: password as a bytestring to generate key
        :return: Encryption key, salt
        """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    encryption_key = base64.urlsafe_b64encode(kdf.derive(password))
    return encryption_key


def write_key_to_file(filename: str, encryption_key: bytes):
    with open(filename, 'wb') as keyfile:
        keyfile.write(encryption_key)


def write_salt_to_file(filename: str, salt: bytes):
    with open(filename, 'wb') as salt_file:
        salt_file.write(salt)


def read_keyfile(filename: str) -> object:
    with open(filename, 'rb') as keyfile:
        key = keyfile.read()
        fernet = Fernet(key)
        return fernet


def read_salt_file(filename: str) -> bytes:
    with open(filename, 'rb') as salt_file:
        salt = salt_file.read()
        return salt


def generate_fernet(key: bytes) -> object:
    fernet = Fernet(key)
    return fernet


def encrypt_file(file_to_encrypt: str, fernet: object):
    with open(file_to_encrypt, 'rb') as file:
        original = file.read()
        encrypted = fernet.encrypt(original)
    with open(file_to_encrypt, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)


def decrypt_file(file_to_decrypt: str, fernet: object):
    with open(file_to_decrypt, 'rb') as file:
        original = file.read()
        decrypted = fernet.decrypt(original)
    with open(file_to_decrypt, 'wb') as encrypted_file:
        encrypted_file.write(decrypted)
