import os
from pathlib import Path


DATA_DIR = Path(os.getenv("EARNETICS_CRM_DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / os.getenv("EARNETICS_CRM_DB_FILE", "earnetics_crm.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Basic defaults
DEFAULT_PIPELINES = {
    "real_estate": ["new", "contacted", "negotiating", "under_contract", "closed", "lost"],
    "automation_clients": ["new", "contacted", "demo_scheduled", "proposal", "closed_won", "closed_lost"],
}
