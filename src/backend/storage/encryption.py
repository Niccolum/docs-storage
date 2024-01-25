import os
from io import BytesIO
from typing import BinaryIO

from Cryptodome.Cipher import AES

from backend.core.settings import get_settings


def encrypt(raw_file: BinaryIO) -> tuple[BytesIO, bytes]:
    aes_key = _get_aes_key()

    cipher = AES.new(key=aes_key, mode=AES.MODE_EAX)
    encrypted_file = BytesIO()

    while True:
        chunk = raw_file.read(1024 * AES.block_size)
        if not chunk:
            _ = encrypted_file.write(cipher.digest())
            _ = encrypted_file.seek(os.SEEK_SET)
            _ = raw_file.seek(os.SEEK_SET)

            return encrypted_file, cipher.nonce

        encrypted_chunk = cipher.encrypt(chunk)
        _ = encrypted_file.write(encrypted_chunk)


def decrypt(encrypted_file: BinaryIO, nonce: bytes) -> BytesIO:
    aes_key = _get_aes_key()

    cipher = AES.new(key=aes_key, mode=AES.MODE_EAX, nonce=nonce)
    raw_file = BytesIO()

    digest = _get_digest(encrypted_file)
    while True:
        encrypted_chunk = encrypted_file.read(1024 * AES.block_size)
        if not encrypted_chunk:
            cipher.verify(digest)
            _ = raw_file.seek(os.SEEK_SET)
            return raw_file

        chunk = cipher.decrypt(encrypted_chunk)
        _ = raw_file.write(chunk)


def _get_digest(encrypted_file: BinaryIO) -> bytes:
    encrypted_data_size = encrypted_file.seek(-AES.block_size, os.SEEK_END)  # Note minus sign
    digest = encrypted_file.read()
    _ = encrypted_file.truncate(encrypted_data_size)
    _ = encrypted_file.seek(os.SEEK_SET)
    return digest


def _get_aes_key() -> bytes:
    settings = get_settings()
    return settings.security.aes_key


if __name__ == "__main__":
    from backend.storage.constants import PDF_THUMBNAIL

    example_raw_file_path = PDF_THUMBNAIL
    decrypted_file_path = PDF_THUMBNAIL.parent / f"decrypted-{PDF_THUMBNAIL.name}"

    with example_raw_file_path.open("rb") as raw_file:
        encrypt_file, nonce = encrypt(raw_file)

    decrypted_file = decrypt(encrypt_file, nonce)
    with decrypted_file_path.open("wb") as f:
        _ = f.write(decrypted_file.getbuffer())
