"""Test bootstrap.

Adds the backend dir to sys.path and pins a single session-wide SQLite database
BEFORE any app module imports — the SQLAlchemy engine binds at import time, so
every API test module must share one database rather than each juggling its own
(which would rebind a stale engine and cross-contaminate).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Bind the engine to a dedicated, clean test DB for the whole session.
_TEST_DB = os.path.join(os.path.dirname(__file__), "_pytest_dealproof.db")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TEST_DB}")
os.environ.setdefault("ENV", "development")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
