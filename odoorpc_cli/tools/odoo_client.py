from __future__ import annotations

import urllib.parse
from typing import Any

import odoorpc

from ..settings import Settings


class OdooClient:
    """
    A thin Odoo JSON-RPC client using odoorpc (mirrors patterns from biszx-odoo-mcp)
    """

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
        self._connect()

    def _connect(self) -> None:
        protocol = "jsonrpc+ssl" if self.is_https else "jsonrpc"
        port = self.port or (443 if self.is_https else 80)
        self.odoo = odoorpc.ODOO(
            self.hostname, protocol=protocol, port=port, timeout=self.timeout
        )
        # login will raise on auth failure
        self.odoo.login(self.db, self.username, self.password)

        # fetch user info
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

    def get_current_user(self) -> dict:
        """Return the current authenticated user's information."""
        return getattr(self, "user", {})

    def model_search(self, query: str) -> dict:
        IrModel = self.odoo.env["ir.model"]
        domain = ["|", ("model", "like", query), ("name", "like", query)]
        models = (
            IrModel.search_read(domain, ["model", "name"])
            if hasattr(IrModel, "search_read")
            else []
        )
        return {"length": len(models), "models": models}

    def model_field(self, model: str):
        m = self.odoo.env[model]
        return m.fields_get()

    def search_read(
        self,
        model: str,
        domain: list[Any],
        fields: list[str],
        order: str | None = None,
        offset: int = 0,
        limit: int | None = None,
    ):
        m = self.odoo.env[model]
        return m.search_read(
            domain, fields=fields, order=order, offset=offset, limit=limit
        )

    def search_count(self, model: str, domain: list[Any]):
        m = self.odoo.env[model]
        try:
            return m.search_count(domain)
        except Exception:
            return len(m.search(domain))

    def create(self, model: str, vals: list[dict]):
        m = self.odoo.env[model]
        return m.create(vals)

    def write(self, model: str, ids: list[int], vals: dict):
        m = self.odoo.env[model]
        return m.write(ids, vals)

    def unlink(self, model: str, ids: list[int]):
        m = self.odoo.env[model]
        return m.unlink(ids)

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
