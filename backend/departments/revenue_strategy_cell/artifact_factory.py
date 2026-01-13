"""Artifact Factory - creates tangible output files from strategy plays."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.corporate_memory import BUSINESS_DB_PATH

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RUNS_DIR = PROJECT_ROOT / "runs"


class ArtifactFactory:
    """Creates artifact files from strategy plays."""

    def __init__(self, db_path: Path = BUSINESS_DB_PATH):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create strategy_artifacts table if it doesn't exist."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategy_artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    play_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_artifacts(self, run_id: str, plays: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create artifacts for all plays in a run."""
        artifacts = []
        
        for play in plays:
            play_id = play.get("play_id", "unknown")
            play_artifacts = self.create_play_artifacts(run_id, play_id, play)
            artifacts.extend(play_artifacts)
        
        return artifacts

    def create_play_artifacts(
        self, run_id: str, play_id: str, play: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create artifacts for a single play."""
        artifacts_dir = RUNS_DIR / run_id / "artifacts" / "strategy"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        artifacts = []
        
        # 1. Offer one-pager
        offer_file = artifacts_dir / f"{play_id}_offer_one_pager.md"
        with open(offer_file, "w", encoding="utf-8") as f:
            f.write(f"# {play.get('title', 'Offer')}\n\n")
            f.write(f"## Target Buyer\n{play.get('target_buyer', 'N/A')}\n\n")
            f.write(f"## Offer\n")
            for item in play.get("offer", []):
                f.write(f"- {item}\n")
            f.write(f"\n## Price Points\n")
            for pp in play.get("price_points", []):
                f.write(f"- ${pp.get('amount')}: {pp.get('label')}\n")
            f.write(f"\n## Guarantee\n{play.get('guarantee_or_risk_reversal', 'N/A')}\n")
        
        self._record_artifact(run_id, play_id, "offer_one_pager", str(offer_file))
        artifacts.append({"type": "offer_one_pager", "file": str(offer_file)})
        
        # 2. Landing page draft
        landing_file = artifacts_dir / f"{play_id}_landing_page_draft.md"
        with open(landing_file, "w", encoding="utf-8") as f:
            f.write(f"# {play.get('title', 'Offer')} - Landing Page\n\n")
            f.write(f"## Hero Section\n")
            f.write(f"Headline: {play.get('title', 'N/A')}\n")
            f.write(f"Subheadline: {play.get('target_buyer', 'N/A')}\n\n")
            f.write(f"## Key Benefits\n")
            for item in play.get("offer", [])[:3]:
                f.write(f"- {item}\n")
            f.write(f"\n## Social Proof\n")
            f.write(f"Guarantee: {play.get('guarantee_or_risk_reversal', 'N/A')}\n")
            f.write(f"\n## Call to Action\n")
            f.write(f"Primary CTA: Book a call / Get started\n")
        
        self._record_artifact(run_id, play_id, "landing_page_draft", str(landing_file))
        artifacts.append({"type": "landing_page_draft", "file": str(landing_file)})
        
        # 3. Outreach scripts
        scripts_file = artifacts_dir / f"{play_id}_outreach_scripts.txt"
        with open(scripts_file, "w", encoding="utf-8") as f:
            scripts = play.get("outreach_script", {})
            f.write("=== DM SCRIPT ===\n")
            f.write(f"{scripts.get('dm', 'N/A')}\n\n")
            f.write("=== EMAIL SCRIPT ===\n")
            f.write(f"{scripts.get('email', 'N/A')}\n\n")
            f.write("=== CALL OPENER ===\n")
            f.write(f"{scripts.get('call_opener', 'N/A')}\n")
        
        self._record_artifact(run_id, play_id, "outreach_scripts", str(scripts_file))
        artifacts.append({"type": "outreach_scripts", "file": str(scripts_file)})
        
        # 4. Follow-up sequence
        followup_file = artifacts_dir / f"{play_id}_follow_up_sequence.txt"
        with open(followup_file, "w", encoding="utf-8") as f:
            followups = play.get("outreach_script", {}).get("follow_up_5", [])
            for i, followup in enumerate(followups, 1):
                f.write(f"Follow-up {i}:\n{followup}\n\n")
        
        self._record_artifact(run_id, play_id, "follow_up_sequence", str(followup_file))
        artifacts.append({"type": "follow_up_sequence", "file": str(followup_file)})
        
        # 5. Lead source plan
        leadplan_file = artifacts_dir / f"{play_id}_lead_source_plan.md"
        with open(leadplan_file, "w", encoding="utf-8") as f:
            channels = play.get("acquisition_channel", {})
            f.write(f"# Lead Source Plan: {play.get('title', 'Offer')}\n\n")
            f.write(f"## Primary Channel\n{channels.get('primary', 'N/A')}\n\n")
            f.write(f"## Secondary Channel\n{channels.get('secondary', 'N/A')}\n\n")
            f.write(f"## Daily Activity Quota\n")
            quota = play.get("daily_activity_quota", {})
            f.write(f"- DMs: {quota.get('dms', 0)}\n")
            f.write(f"- Emails: {quota.get('emails', 0)}\n")
            f.write(f"- Calls: {quota.get('calls', 0)}\n")
            f.write(f"- Posts: {quota.get('posts', 0)}\n")
        
        self._record_artifact(run_id, play_id, "lead_source_plan", str(leadplan_file))
        artifacts.append({"type": "lead_source_plan", "file": str(leadplan_file)})
        
        return artifacts

    def _record_artifact(
        self, run_id: str, play_id: str, artifact_type: str, filepath: str
    ) -> None:
        """Record artifact in database."""
        import sqlite3
        now = datetime.now(timezone.utc).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO strategy_artifacts
                (run_id, play_id, artifact_type, filepath, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (run_id, play_id, artifact_type, filepath, now))
            conn.commit()

