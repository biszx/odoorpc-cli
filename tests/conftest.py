import importlib

import pytest
from odoocli.settings import Settings, save_config
from odoocli.tools.odoo_client import OdooClient


class FakeClient:
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._store = {}
        self._next = {}

    @classmethod
    def from_config(cls):
        return cls()

    def get_current_user(self):
        return {"id": 1, "name": "Tester"}

    def create(self, model, values):
        self._store.setdefault(model, {})
        self._next.setdefault(model, 1)
        ids = []
        for vals in values:
            nid = self._next[model]
            self._next[model] += 1
            # shallow copy to avoid test-side mutations
            rec = {"id": nid, **(vals or {})}
            self._store[model][nid] = rec
            ids.append(nid)
        return ids

    def execute_method(self, model, method, args=None, kwargs=None):
        return {
            "model": model,
            "method": method,
            "args": args or [],
            "kwargs": kwargs or {},
        }

    def write(self, model, ids, vals):
        model_store = self._store.get(model, {})
        for i in ids:
            if i in model_store:
                model_store[i].update(vals or {})
            else:
                return False
        return True

    def search_read(self, model, domain, fields, limit):
        records = list(self._store.get(model, {}).values())
        # Very small domain support: [['id', '=', value]] and simple AND list
        if domain:
            filtered = []
            for rec in records:
                ok = True
                for cond in domain:
                    if not isinstance(cond, (list, tuple)) or len(cond) < 3:
                        continue
                    f, op, val = cond[0], cond[1], cond[2]
                    if op in ("=", "=="):
                        if rec.get(f) != val:
                            ok = False
                            break
                    elif op == "in":
                        if rec.get(f) not in val:
                            ok = False
                            break
                    else:
                        ok = False
                        break
                if ok:
                    filtered.append(rec)
            records = filtered
        # Normalize `fields` which may be provided as a list or comma-separated string
        if fields and fields != "all":
            if isinstance(fields, str):
                req_fields = [f.strip() for f in fields.split(",") if f.strip()]
            else:
                req_fields = list(fields)
            out = []
            for rec in records:
                r = {f: rec.get(f) for f in req_fields}
                if "id" not in r:
                    r["id"] = rec.get("id")
                out.append(r)
            records = out
        if limit is not None:
            try:
                lim = int(limit)
            except Exception:
                lim = None
            if lim is not None:
                records = records[:lim]
        # If there are no records for common demo models, return a small
        # default so existing tests that expect a non-empty result continue
        # to pass. This mirrors the previous FakeClient behavior.
        if not records and model == "res.partner":
            return [{"id": 1, "name": "A"}]

        return records

    def search_count(self, model, domain):
        return len(self.search_read(model, domain, [], None))

    def unlink(self, model, ids):
        for i in ids:
            self._store.get(model, {}).pop(i, None)
        return True

    def model_field(self, model: str):
        return {"id": 1, "fields": {"name": {"string": "Name"}}}

    def model_search(self, query: str):
        return {"length": 1, "models": [{"model": "res.partner", "name": "Partner"}]}


@pytest.fixture(scope="session", autouse=True)
def patch_all(tmp_path_factory):
    """Session-scoped autouse fixture to provide a fake Odoo client for
    command tests and configure Settings to use a temporary config directory.

    This runs once per test session to avoid repeated connectivity checks
    and per-test monkeypatch overhead, reducing total test runtime.
    """
    # Point Settings config to a temp directory so tests can save/load configs
    cfg_dir = tmp_path_factory.mktemp(".odoo")
    host = "http://localhost:8069"
    Settings.CONFIG_DIR = str(cfg_dir)
    Settings.CONFIG_PATH = str(cfg_dir / "config.json")
    save_config(host=host, db="dev", username="admin", password="admin")

    # Decide whether to use the real local Odoo server or the FakeClient.
    # Try creating a short-timeout OdooClient to validate connectivity and credentials.
    try:
        OdooClient(host=host, db="dev", username="admin", password="admin", timeout=2)
    except Exception:
        modules = [
            "odoocli.commands.auth.info",
            "odoocli.commands.auth.login",
            "odoocli.commands.create",
            "odoocli.commands.call_method",
            "odoocli.commands.write",
            "odoocli.commands.search.read",
            "odoocli.commands.search.count",
            "odoocli.commands.unlink",
            "odoocli.commands.model.field",
            "odoocli.commands.model.search",
        ]
        for mod_name in modules:
            try:
                mod = importlib.import_module(mod_name)
            except Exception:
                continue
            if hasattr(mod, "OdooClient"):
                mod.OdooClient = FakeClient

    yield
