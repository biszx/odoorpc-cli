from __future__ import annotations

import functools
import os
import pickle
import urllib.parse
from http.cookiejar import CookieJar
from typing import Any
from urllib.request import HTTPCookieProcessor, Request, build_opener

import click
import odoorpc
import odoorpc.env
import odoorpc.error

from ..settings import Settings


class BrowserOpener:
    def __init__(self):
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))

    def open(self, *args, **kwargs):
        req = args[0] if args else kwargs.get("request", kwargs.get("url"))
        if isinstance(req, str):
            req = Request(req)
        if not req.headers.get("User-agent"):
            req.add_header(
                "User-Agent",
                (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )
        return self._opener.open(req, **kwargs)


def is_auth_error(exc: Exception) -> bool:
    if isinstance(exc, odoorpc.error.InternalError):
        return True
    if isinstance(exc, odoorpc.error.RPCError):
        msg = str(exc).lower()
        return any(k in msg for k in ("session expired", "access denied", "not logged"))
    return False


def with_reauth(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as exc:
            if not is_auth_error(exc):
                raise
            try:
                self._connect()
                self._save_session()
            except Exception as login_exc:
                raise SystemExit(
                    f"Authentication failed. Run 'odoo auth login' to re-authenticate. ({login_exc})"
                ) from login_exc
            try:
                return method(self, *args, **kwargs)
            except Exception:
                raise SystemExit(
                    "Session refreshed but the request still failed. "
                    "Run 'odoo auth login' to re-authenticate."
                ) from None

    return wrapper


class OdooClient:
    def __init__(
        self, host: str, db: str, username: str, password: str, timeout: int = 30
    ):
        self.host = host.rstrip("/")
        self.db = db
        self.username = username
        self.password = password
        self.timeout = timeout
        parsed = urllib.parse.urlparse(self.host)
        self.hostname = parsed.hostname or "localhost"
        self.port = parsed.port
        self.is_https = parsed.scheme == "https"

        if not self._try_load_session():
            self._connect()
            self._save_session()

    def __getstate__(self) -> dict:
        state = self.__dict__.copy()
        state.pop("password", None)
        odoo = state.pop("odoo", None)
        if odoo is not None:
            state["_odoo_cache"] = {
                "uid": self.uid,
                "context": dict(odoo.env.context),
                "version": odoo.version,
            }
        return state

    def __setstate__(self, state: dict) -> None:
        self._odoo_cache = state.pop("_odoo_cache", None)
        self.__dict__.update(state)

    def _restore_odoo(self) -> None:
        odoo_cache = self._odoo_cache
        protocol = "jsonrpc+ssl" if self.is_https else "jsonrpc"
        port = self.port or (443 if self.is_https else 80)
        self.odoo = odoorpc.ODOO(
            self.hostname,
            protocol=protocol,
            port=port,
            timeout=self.timeout,
            version=odoo_cache["version"],
            opener=BrowserOpener(),
        )
        self.odoo._env = odoorpc.env.Environment(
            self.odoo, self.db, odoo_cache["uid"], odoo_cache["context"]
        )
        self.odoo._login = self.username
        self.odoo._password = self.password

    def _session_key(self) -> str:
        port = self.port or (443 if self.is_https else 80)
        return f"{self.db}_{self.username}_{self.hostname}_{port}"

    def _try_load_session(self) -> bool:
        try:
            with open(Settings.SESSION_CACHE_PATH, "rb") as f:
                cache: dict = pickle.load(f)
            cached: OdooClient = cache.get(self._session_key())
            if cached is None:
                return False
            cached.password = self.password
            cached._restore_odoo()
            self.odoo = cached.odoo
            self.odoo._password = self.password
            self.odoo._login = self.username
            self.uid = cached.uid
            self.user = cached.user
            return True
        except Exception:
            return False

    def _save_session(self) -> None:
        Settings.ensure_dir()
        cache: dict = {}
        try:
            with open(Settings.SESSION_CACHE_PATH, "rb") as f:
                cache = pickle.load(f)
        except Exception:
            pass
        cache[self._session_key()] = self
        try:
            with open(Settings.SESSION_CACHE_PATH, "wb") as f:
                pickle.dump(cache, f)
            os.chmod(Settings.SESSION_CACHE_PATH, 0o600)
        except Exception as exc:
            click.echo(f"Warning: could not cache session ({exc})", err=True)

    def _fetch_user(self) -> None:
        user_model = self.odoo.env["res.users"]
        self.user = user_model.search_read(
            [("login", "=", self.username)],
            [
                "id",
                "name",
                "login",
                "email",
                "lang",
                "tz",
                "company_id",
                "partner_id",
                "employee_ids",
            ],
            limit=1,
        )[0]
        self.uid = self.user["id"]

    def _connect(self) -> None:
        protocol = "jsonrpc+ssl" if self.is_https else "jsonrpc"
        port = self.port or (443 if self.is_https else 80)
        self.odoo = odoorpc.ODOO(
            self.hostname,
            protocol=protocol,
            port=port,
            timeout=self.timeout,
            opener=BrowserOpener(),
        )
        self.odoo.login(self.db, self.username, self.password)
        self._fetch_user()

    def get_current_user(self) -> dict:
        return getattr(self, "user", {})

    @with_reauth
    def model_search(self, query: str) -> dict:
        IrModel = self.odoo.env["ir.model"]
        domain = ["|", ("model", "like", query), ("name", "like", query)]
        models = (
            IrModel.search_read(domain, ["model", "name"])
            if hasattr(IrModel, "search_read")
            else []
        )
        return {"length": len(models), "models": models}

    @with_reauth
    def model_field(self, model: str):
        return self.odoo.env[model].fields_get()

    @with_reauth
    def search_read(
        self,
        model: str,
        domain: list[Any],
        fields: list[str],
        order: str | None = None,
        offset: int = 0,
        limit: int | None = None,
    ):
        return self.odoo.env[model].search_read(
            domain, fields=fields, order=order, offset=offset, limit=limit
        )

    @with_reauth
    def search_count(self, model: str, domain: list[Any]):
        m = self.odoo.env[model]
        try:
            return m.search_count(domain)
        except Exception:
            return len(m.search(domain))

    @with_reauth
    def create(self, model: str, vals: list[dict]):
        return self.odoo.env[model].create(vals)

    @with_reauth
    def write(self, model: str, ids: list[int], vals: dict):
        return self.odoo.env[model].write(ids, vals)

    @with_reauth
    def unlink(self, model: str, ids: list[int]):
        return self.odoo.env[model].unlink(ids)

    @with_reauth
    def execute_method(
        self,
        model: str,
        method: str,
        args: list | None = None,
        kwargs: dict | None = None,
    ):
        m = self.odoo.env[model]
        func = getattr(m, method)
        if kwargs:
            return func(*(args or []), **(kwargs or {}))
        return func(*(args or []))

    @classmethod
    def from_config(cls):
        host, db, username, password = Settings.load()
        return cls(host=host, db=db, username=username, password=password)
