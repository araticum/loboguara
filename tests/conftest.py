import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent

if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:55432/eventsaas")
os.environ.setdefault("REDIS_URL", "redis://localhost:56379/0")
os.environ.setdefault("SERIEMA_DB_SCHEMA", "seriema")
os.environ.setdefault("SERIEMA_REDIS_DB", "5")
os.environ.setdefault("SERIEMA_OPS_MAX_LIMIT", "100")
os.environ.setdefault("VOICE_WEBHOOK_MAX_AGE_SECONDS", "300")
os.environ.setdefault("SERIEMA_DLQ_REPLAY_DRY_RUN", "true")
