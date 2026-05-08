import base64
import hashlib
import json
import os
import platform
import uuid

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Settings:
    """
    Manage ~/.odoo/config.json
    """

    CONFIG_DIR = os.path.expanduser("~/.odoo")
    CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
    _purpose = b"odoo-cli-machine-key"

    @classmethod
    def ensure_dir(cls) -> None:
        if not os.path.isdir(cls.CONFIG_DIR):
            os.makedirs(cls.CONFIG_DIR, exist_ok=True)

    @classmethod
    def _get_salt(cls) -> bytes:
        node = platform.node() or ""
        mac = str(uuid.getnode())
        raw = (node + mac).encode("utf-8")
        return hashlib.sha256(raw).digest()

    @classmethod
    def _derive_key(cls) -> bytes:
        salt = cls._get_salt()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = kdf.derive(cls._purpose)
        return base64.urlsafe_b64encode(key)

    @classmethod
    def encrypt_password(cls, plain: str) -> str:
        key = cls._derive_key()
        f = Fernet(key)
        return f.encrypt(plain.encode("utf-8")).decode("utf-8")

    @classmethod
    def decrypt_password(cls, token: str) -> str:
        key = cls._derive_key()
        f = Fernet(key)
        return f.decrypt(token.encode("utf-8")).decode("utf-8")

    @classmethod
    def save(cls, host: str, db: str, username: str, password: str) -> None:
        cls.ensure_dir()
        token = cls.encrypt_password(password)
        conf = {
            "host": host,
            "db": db,
            "username": username,
            "password_encrypted": token,
        }
        with open(cls.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(conf, f, indent=2)

    @classmethod
    def load(cls) -> tuple[str, str, str, str]:
        cls.ensure_dir()
        if not os.path.isfile(cls.CONFIG_PATH):
            raise RuntimeError('Config not found; run "odoo auth" first')
        with open(cls.CONFIG_PATH, encoding="utf-8") as f:
            conf = json.load(f)
        host = conf.get("host")
        db = conf.get("db")
        username = conf.get("username")
        token = conf.get("password_encrypted")
        if token is None:
            raise RuntimeError("Encrypted password missing from config")
        password = cls.decrypt_password(token)
        return host, db, username, password


# Backwards-compatible module-level functions
def ensure_config_exists() -> None:
    Settings.ensure_dir()


def save_config(host: str, db: str, username: str, password: str) -> None:
    Settings.save(host, db, username, password)


def load_config() -> tuple[str, str, str, str]:
    return Settings.load()
