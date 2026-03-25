import os
import sys
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent

if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

# Ensure `from Seriema import ...` works on case-sensitive runners (Linux CI),
# regardless of the checkout folder name casing.
if "Seriema" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "Seriema",
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules["Seriema"] = module
        spec.loader.exec_module(module)

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:55432/eventsaas")
os.environ.setdefault("REDIS_URL", "redis://localhost:56379/0")
os.environ.setdefault("SERIEMA_DB_SCHEMA", "seriema")
os.environ.setdefault("SERIEMA_REDIS_DB", "5")
os.environ.setdefault("SERIEMA_OPS_MAX_LIMIT", "100")
os.environ.setdefault("VOICE_WEBHOOK_MAX_AGE_SECONDS", "300")
os.environ.setdefault("SERIEMA_DLQ_REPLAY_DRY_RUN", "true")
