import types
from types import SimpleNamespace

from odoocli.tools.odoo_client import OdooClient


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
    from odoocli.settings import Settings as S

    S.load = classmethod(lambda cls=None: ("mh", "md", "mu", "mp"))

    # Reload the odoo_client module so its `from ..settings import ...`
    # bindings pick up our patched Settings.load
    import odoocli.tools.odoo_client as OC

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
