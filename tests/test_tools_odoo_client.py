import pickle
import types
from types import SimpleNamespace

import odoorpc.error
import pytest

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
        def search_read(self, domain, fields=None, order=None, offset=None, limit=None):
            return [{"id": 42, "name": "Tester"}]

    class FakeModelM:
        def search_read(self, domain, fields=None, order=None, offset=None, limit=None):
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


# --- Session caching tests ---

def _make_client_stub(monkeypatch):
    """Return an OdooClient.__new__ stub with all connection attrs pre-set."""
    import odoorpc_cli.tools.odoo_client as OC

    c = OC.OdooClient.__new__(OC.OdooClient)
    c.host = "http://localhost"
    c.hostname = "localhost"
    c.db = "testdb"
    c.username = "admin"
    c.password = "secret"
    c.timeout = 30
    c.port = 8069
    c.is_https = False
    return c


def _make_cached_client(monkeypatch, uid=7):
    """Build a stub OdooClient that mimics a post-__setstate__ cached object."""
    c = _make_client_stub(monkeypatch)
    c.uid = uid
    c.user = {"id": uid, "name": "Admin", "login": "admin"}
    c.odoo = SimpleNamespace(
        _password="secret",
        _login="admin",
        version="17.0",
        env=SimpleNamespace(context={"lang": "en_US", "tz": "UTC", "uid": uid}),
    )
    return c


def test_try_load_session_returns_false_when_no_file(tmp_path, monkeypatch):
    from odoorpc_cli.settings import Settings

    monkeypatch.setattr(Settings, "SESSION_CACHE_PATH", str(tmp_path / "session_cache.pkl"))
    c = _make_client_stub(monkeypatch)
    assert c._try_load_session() is False


def test_try_load_session_returns_false_on_missing_key(tmp_path, monkeypatch):
    from odoorpc_cli.settings import Settings

    cache = tmp_path / "session_cache.pkl"
    cache.write_bytes(pickle.dumps({"other_key": object()}))
    monkeypatch.setattr(Settings, "SESSION_CACHE_PATH", str(cache))

    c = _make_client_stub(monkeypatch)
    assert c._try_load_session() is False


def test_try_load_session_returns_false_on_bad_pickle(tmp_path, monkeypatch):
    from odoorpc_cli.settings import Settings

    cache = tmp_path / "session_cache.pkl"
    cache.write_bytes(b"not a pickle")
    monkeypatch.setattr(Settings, "SESSION_CACHE_PATH", str(cache))

    c = _make_client_stub(monkeypatch)
    assert c._try_load_session() is False


def test_try_load_session_success(tmp_path, monkeypatch):
    from odoorpc_cli.settings import Settings

    c = _make_client_stub(monkeypatch)
    cached = _make_cached_client(monkeypatch, uid=7)

    cache_file = tmp_path / "session_cache.pkl"
    cache_file.write_bytes(pickle.dumps({c._session_key(): cached}))
    monkeypatch.setattr(Settings, "SESSION_CACHE_PATH", str(cache_file))

    result = c._try_load_session()
    assert result is True
    assert c.uid == 7
    assert c.user["name"] == "Admin"
    # credentials always overwritten with the live values from __init__
    assert c.odoo._password == "secret"
    assert c.odoo._login == "admin"


def test_save_session_writes_pickle_and_sets_permissions(tmp_path, monkeypatch):
    from odoorpc_cli.settings import Settings

    cache = tmp_path / "session_cache.pkl"
    monkeypatch.setattr(Settings, "SESSION_CACHE_PATH", str(cache))
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(tmp_path))

    c = _make_client_stub(monkeypatch)
    c.uid = 3
    c.user = {"id": 3, "name": "Test"}
    c.odoo = SimpleNamespace(
        version="17.0",
        env=SimpleNamespace(context={"lang": "en_US", "tz": "UTC", "uid": 3}),
    )

    c._save_session()

    assert cache.exists()
    assert oct(cache.stat().st_mode)[-3:] == "600"
    saved: dict = pickle.loads(cache.read_bytes())
    key = c._session_key()
    assert key in saved
    restored: object = saved[key]
    assert restored.uid == 3


def test_getstate_excludes_odoo_and_password():
    c = _make_client_stub(None)
    c.uid = 5
    c.user = {"id": 5}
    c.odoo = SimpleNamespace(
        version="17.0",
        env=SimpleNamespace(context={"uid": 5}),
    )
    state = c.__getstate__()
    assert "odoo" not in state
    assert "password" not in state          # plaintext password never persisted
    assert state["_odoo_cache"]["uid"] == 5
    assert state["_odoo_cache"]["version"] == "17.0"


def testis_auth_error_internal_error():
    from odoorpc_cli.tools.odoo_client import is_auth_error
    assert is_auth_error(odoorpc.error.InternalError("Not logged!")) is True


def testis_auth_error_rpc_session_expired():
    from odoorpc_cli.tools.odoo_client import is_auth_error
    assert is_auth_error(odoorpc.error.RPCError("Odoo session expired")) is True


def testis_auth_error_non_auth():
    from odoorpc_cli.tools.odoo_client import is_auth_error
    assert is_auth_error(ValueError("bad domain")) is False
    assert is_auth_error(odoorpc.error.RPCError("Field not found")) is False


def testwith_reauth_no_error():
    from odoorpc_cli.tools.odoo_client import with_reauth

    @with_reauth
    def dummy(self):
        return 42

    assert dummy(_make_client_stub(None)) == 42


def testwith_reauth_reraises_non_auth():
    from odoorpc_cli.tools.odoo_client import with_reauth

    @with_reauth
    def boom(self):
        raise ValueError("domain error")

    with pytest.raises(ValueError, match="domain error"):
        boom(_make_client_stub(None))


def testwith_reauth_relogins_on_auth_error(monkeypatch):
    import odoorpc_cli.tools.odoo_client as OC

    c = _make_client_stub(monkeypatch)
    calls = {"n": 0}

    @OC.with_reauth
    def flaky(self):
        calls["n"] += 1
        if calls["n"] == 1:
            raise odoorpc.error.InternalError("Not logged!")
        return "ok"

    reconnect_calls = {"n": 0}

    def fake_connect(self):
        reconnect_calls["n"] += 1

    monkeypatch.setattr(OC.OdooClient, "_connect", fake_connect)
    monkeypatch.setattr(OC.OdooClient, "_save_session", lambda self: None)

    assert flaky(c) == "ok"
    assert reconnect_calls["n"] == 1


def testwith_reauth_exits_when_relogin_fails(monkeypatch):
    import odoorpc_cli.tools.odoo_client as OC

    c = _make_client_stub(monkeypatch)

    @OC.with_reauth
    def always_auth_error(self):
        raise odoorpc.error.InternalError("Not logged!")

    monkeypatch.setattr(OC.OdooClient, "_connect", lambda self: (_ for _ in ()).throw(RuntimeError("wrong password")))

    with pytest.raises(SystemExit, match="re-authenticate"):
        always_auth_error(c)
