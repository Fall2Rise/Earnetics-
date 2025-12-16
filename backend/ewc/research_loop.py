from __future__ import annotations

import logging
import os
import json
import sqlite3
from typing import Any, Dict
from datetime import datetime

from backend.ewc.revenue_loop import RevenueLoopRunner
from backend.corporate_memory import BUSINESS_DB_PATH
from backend.audit_log import log_event

logger = logging.getLogger(__name__)

class ResearchLoopRunner(RevenueLoopRunner):
    """
    Specialized runner for the Continuous Research Loop.
    Executes the 'continuous_research' flow and saves results to the Library.
    """

    def run_research(self, market_signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the continuous research flow.
        """
        if "continuous_research" not in self.flows:
            logger.error("Flow 'continuous_research' not found in crews.yaml")
            return {}

        logger.info("🔎 Starting Continuous Research Loop...")
        state = {"market_signals": market_signals}

        # Execute the flow
        for step in self.flows["continuous_research"]:
            step_name = step.get("name", "<unnamed>")
            logger.info(f"▶ Running research step: {step_name}")
            state_update = self._run_step(step, state)
            state.update(state_update)

        # Extract the new revenue play
        new_play = state.get("new_revenue_play")
        if new_play:
            logger.info("💡 New Revenue Play Discovered!")
            self._save_to_library(new_play)
            return new_play
        else:
            logger.warning("Research loop completed but no play was generated.")
            return {}

    def _save_to_library(self, play: Dict[str, Any]) -> None:
        """Save the discovered play to the SQLite Library."""
        try:
            with sqlite3.connect(BUSINESS_DB_PATH) as conn:
                cur = conn.cursor()
                
                # Ensure table exists (idempotent)
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS library_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        category TEXT,
                        description TEXT,
                        detailed_playbook TEXT,
                        tags TEXT,
                        created_by_agent TEXT,
                        last_updated TEXT
                    )
                    """
                )

                # Insert new item
                cur.execute(
                    """
                    INSERT INTO library_items (title, category, description, detailed_playbook, tags, created_by_agent, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        play.get("title", "Untitled Research Play"),
                        play.get("category", "Research"),
                        play.get("description", ""),
                        json.dumps(play), # Store full object as playbook
                        json.dumps(play.get("tags", [])),
                        "Innovation Crew",
                        datetime.utcnow().isoformat()
                    )
                )
                item_id = cur.lastrowid
                conn.commit()
                
            log_event("library.auto_created", status="success", details={"id": item_id, "title": play.get("title")})
            logger.info(f"✅ Saved new play to Library (ID: {item_id})")

        except Exception as e:
            logger.exception(f"Failed to save research result to library: {e}")
