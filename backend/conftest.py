"""Make ``app`` importable when running pytest from the backend directory.

Redundant with ``[tool.pytest.ini_options].pythonpath`` but kept so the suite
also runs under older pytest that ignores that setting.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
