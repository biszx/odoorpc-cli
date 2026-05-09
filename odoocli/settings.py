import json
import os

from cryptography.fernet import Fernet


class Settings:
    CONFIG_DIR = os.path.expanduser("~/.odoo")
    CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
    KEY_PATH = os.path.join(CONFIG_DIR, "machine.key")

    @classmethod
    def ensure_dir(cls) -> None:
        if not os.path.isdir(cls.CONFIG_DIR):
            os.makedirs(cls.CONFIG_DIR, exist_ok=True)

    @classmethod
    def _get_or_create_key(cls) -> bytes:
        """Return a persistent Fernet key stored in `~/.odoo/machine.key`.

        The key is created once and written with restrictive permissions (0600).
        """
        cls.ensure_dir()
        if os.path.isfile(cls.KEY_PATH):
            with open(cls.KEY_PATH, "rb") as f:
                return f.read()

        key = Fernet.generate_key()
        # Write atomically and restrict permissions
        temp_path = cls.KEY_PATH + ".tmp"
        with open(temp_path, "wb") as f:
            f.write(key)
        try:
            os.replace(temp_path, cls.KEY_PATH)
            os.chmod(cls.KEY_PATH, 0o600)
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
        return key

    @classmethod
    def encrypt_password(cls, plain: str) -> str:
        key = cls._get_or_create_key()
        f = Fernet(key)
        return f.encrypt(plain.encode("utf-8")).decode("utf-8")

    @classmethod
    def decrypt_password(cls, token: str) -> str:
        key = cls._get_or_create_key()
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
