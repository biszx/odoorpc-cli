import types
from types import SimpleNamespace

from odoorpc_cli.tools.odoo_client import OdooClient


class _FakeModel:
    def __init__(self, sr=None):
        self._sr = sr or []

    def search_read(self, domain, fields=None, limit=None):
        return self._sr

    def search(self, domain):
        return [1, 2, 3]

    def search_count(self, domain):
        raise Exception("boom")


def test_model_search_with_and_without_search_read():
    c = OdooClient.__new__(OdooClient)
    fake_ir = _FakeModel(sr=[{"model": "m", "name": "n"}])
    c.odoo = SimpleNamespace(**{"env": {"ir.model": fake_ir}})
    res = c.model_search("foo")
    assert res["length"] == 1

    # Without search_read attribute
    no_sr = types.SimpleNamespace()
    c.odoo = SimpleNamespace(**{"env": {"ir.model": no_sr}})
    res2 = c.model_search("foo")
    assert res2["length"] == 0


def test_search_count_fallback_on_exception():
    c = OdooClient.__new__(OdooClient)
    fake = _FakeModel()
    # model name 'x' maps to fake model
    c.odoo = SimpleNamespace(**{"env": {"x": fake}})
    # search_count will raise and fallback returns len(search(domain))
    assert c.search_count("x", []) == 3


def test_execute_method_with_args_and_kwargs():
    c = OdooClient.__new__(OdooClient)

    class M:
        def foo(self, *a, **k):
            return {"args": a, "kwargs": k}

    c.odoo = SimpleNamespace(**{"env": {"m": M()}})
    out1 = c.execute_method("m", "foo", args=[1, 2], kwargs={"x": 3})
    assert out1["args"] == (1, 2)
    assert out1["kwargs"] == {"x": 3}


def test_execute_method_without_kwargs():
    c = OdooClient.__new__(OdooClient)

    class M:
        def bar(self, *a):
            return {"args": a}

    c.odoo = SimpleNamespace(**{"env": {"m": M()}})
    out = c.execute_method("m", "bar", args=[9, 8], kwargs=None)
    assert out["args"] == (9, 8)


def test_create_write_unlink_and_model_field():
    c = OdooClient.__new__(OdooClient)

    class M:
        def __init__(self):
            self._store = {}
            self._next = 1

        def create(self, vals):
            nid = self._next
            self._next += 1
            rec = {"id": nid, **(vals[0] if vals else {})}
            self._store[nid] = rec
            return nid

        def write(self, ids, vals):
            for i in ids:
                if i not in self._store:
                    return False
                self._store[i].update(vals)
            return True

        def unlink(self, ids):
            for i in ids:
                self._store.pop(i, None)
            return True

        def fields_get(self):
            return {"name": {"string": "Name"}}

    m = M()
    c.odoo = SimpleNamespace(**{"env": {"m": m}})

    created = c.create("m", [{"name": "A"}])
    assert created == 1
    assert c.write("m", [1], {"name": "B"}) is True
    assert c.unlink("m", [1]) is True
    assert isinstance(c.model_field("m"), dict)


def test_from_config_module_level_monkeypatch(monkeypatch):
    # Ensure from_config uses the module-level imports (ensure_config_exists, load_config)
    import importlib

    # Patch the Settings.load implementation so that when odoo_client imports
    # module-level functions they will point to the patched implementation.
    from odoorpc_cli.settings import Settings as S

    S.load = classmethod(lambda cls=None: ("mh", "md", "mu", "mp"))

    # Reload the odoo_client module so its `from ..settings import ...`
    # bindings pick up our patched Settings.load
    import odoorpc_cli.tools.odoo_client as OC

    importlib.reload(OC)

    saved_init = OC.OdooClient.__init__
    try:
        # prevent real __init__ side-effects
        OC.OdooClient.__init__ = lambda self, host, db, username, password, timeout=30: (
            None
        )
        c = OC.OdooClient.from_config()
        assert isinstance(c, OC.OdooClient)
    finally:
        OC.OdooClient.__init__ = saved_init


def test_connect_fetches_user_and_search_read(monkeypatch):
    import odoorpc_cli.tools.odoo_client as OC

    class FakeUserModel:
        def search_read(self, domain, fields=None, order=None, limit=None):
            return [{"id": 42, "name": "Tester"}]

    class FakeModelM:
        def search_read(self, domain, fields=None, order=None, limit=None):
            return [{"id": 7, "name": "ModelName"}]

    class FakeODOO:
        def __init__(self, hostname, protocol=None, port=None, timeout=None):
            self.hostname = hostname
            self.protocol = protocol
            self.port = port
            self.timeout = timeout
            self.env = {"res.users": FakeUserModel(), "m": FakeModelM()}

        def login(self, db, username, password):
            self.logged = (db, username, password)

    # Patch the module's odoorpc.ODOO to return our fake implementation
    monkeypatch.setattr(OC, "odoorpc", types.SimpleNamespace(ODOO=FakeODOO))

    c = OC.OdooClient.__new__(OC.OdooClient)
    c.db = "db"
    c.username = "u"
    c.password = "p"
    c.timeout = 5
    c.hostname = "host"
    c.port = 80
    c.is_https = False

    c._connect()

    assert c.uid == 42
    assert c.get_current_user()["name"] == "Tester"

    res = c.search_read("m", [], ["id", "name"], None)
    assert isinstance(res, list)
    assert res[0]["id"] == 7
