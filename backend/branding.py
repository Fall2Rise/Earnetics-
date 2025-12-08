from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / 'config'
BRANDING_PATH = CONFIG_DIR / 'branding.json'
STATIC_BRANDING_DIR = PROJECT_ROOT / 'static' / 'branding'

DEFAULT_BRANDING: Dict[str, Any] = {
    'name': 'AI Revenue Command Center',
    'tagline': 'Autonomous revenue divisions under your command',
    'logo_url': '/static/branding/default-logo.svg',
    'primary_color': '#00f5d4',
    'accent_color': '#4facfe',
    'background_style': 'linear-gradient(135deg, #05060f 0%, #0e1535 60%, #061028 100%)',
    'dashboard_message': 'Your AI departments are synced and generating live revenue.',
    'custom_dashboard_html': '',
    'custom_css': ''
}


def ensure_branding_file() -> None:
    """Make sure the branding config and static directories exist."""

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_BRANDING_DIR.mkdir(parents=True, exist_ok=True)
    if not BRANDING_PATH.exists():
        BRANDING_PATH.write_text(json.dumps(DEFAULT_BRANDING, indent=2), encoding='utf-8')


def load_branding() -> Dict[str, Any]:
    """Load branding configuration, falling back to defaults."""

    ensure_branding_file()
    try:
        data = json.loads(BRANDING_PATH.read_text(encoding='utf-8-sig'))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f'Branding configuration is invalid: {exc}')

    merged = DEFAULT_BRANDING.copy()
    merged.update({k: v for k, v in data.items() if v is not None})
    return merged


def save_branding(branding: Dict[str, Any]) -> Dict[str, Any]:
    """Persist the supplied branding payload, merged with defaults."""

    ensure_branding_file()
    merged = DEFAULT_BRANDING.copy()
    merged.update({k: v for k, v in branding.items() if v is not None})
    BRANDING_PATH.write_text(json.dumps(merged, indent=2), encoding='utf-8')
    return merged


def update_branding(patch: Dict[str, Any]) -> Dict[str, Any]:
    """Apply a partial update to the branding configuration."""

    current = load_branding()
    current.update({k: v for k, v in patch.items() if v is not None})
    BRANDING_PATH.write_text(json.dumps(current, indent=2), encoding='utf-8')
    return current


def reset_branding() -> Dict[str, Any]:
    """Restore the default branding configuration."""

    BRANDING_PATH.write_text(json.dumps(DEFAULT_BRANDING, indent=2), encoding='utf-8')
    return DEFAULT_BRANDING.copy()
