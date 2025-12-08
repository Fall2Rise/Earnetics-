import sqlite3
from datetime import datetime
from typing import Any, Dict

from backend.atom_doctrine import ATOM_DOCTRINE
from backend.prime_directive import load_prime_directive


class AtomDoctrineMutation:
    def __init__(self, vector_db="vector_memory.db", audit_log="audit_log.db"):
        self.vector_db = vector_db
        self.audit_log = audit_log
        self.prime_directive = self._load_prime_directive_snapshot()

    def propose_mutation(self, new_directive: str) -> Dict[str, Any]:
        if self._conflicts_with_prime(new_directive):
            self._log_violation(new_directive)
            return {
                "status": "rejected",
                "reason": "Conflicts with Prime Directive",
                "prime_directive": self.prime_directive,
            }

        self._store_mutation(new_directive)
        return {
            "status": "accepted",
            "directive": new_directive,
        }

    def _conflicts_with_prime(self, directive: str) -> bool:
        # Basic heuristic placeholder – can be replaced with LLM policy checks later.
        keywords = [
            "divest",
            "surrender",
            "cede control",
            "loss",
            "destroy",
            "weaken",
            "donate",
            "revoke",
        ]
        lowered = directive.lower()
        return any(word in lowered for word in keywords)

    def _store_mutation(self, directive: str) -> None:
        conn = sqlite3.connect(self.vector_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO vectors (title, content, tag)
            VALUES (?, ?, ?)
            """,
            ("Doctrine Mutation", directive, "doctrine_mutation"),
        )
        conn.commit()
        conn.close()

    def _log_violation(self, directive: str) -> None:
        conn = sqlite3.connect(self.audit_log)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_log (timestamp, agent, action, context)
            VALUES (?, ?, ?, ?)
            """,
            (datetime.utcnow(), "ATOM_DOCTRINE_MUTATION", "REJECTED_MUTATION", directive),
        )
        conn.commit()
        conn.close()

    def _load_prime_directive_snapshot(self) -> Dict[str, Any]:
        """Snapshot the Prime Directive once; fall back to doctrine if unavailable."""
        try:
            return load_prime_directive().data
        except Exception as exc:  # pragma: no cover - defensive guardrail
            return {
                "status": "unavailable",
                "reason": str(exc),
                "fallback_doctrine": ATOM_DOCTRINE,
            }