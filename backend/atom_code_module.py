import os
import sqlite3
from datetime import datetime

class AtomCodeEngine:
    def __init__(self, base_dir="backend/"):
        self.base_dir = base_dir
        self.audit_log = "audit_log.db"

    def modify_file(self, filepath: str, new_code: str):
        full_path = os.path.join(self.base_dir, filepath)
        with open(full_path, "w") as f:
            f.write(new_code)
        self._log(filepath, "modified")

    def append_to_file(self, filepath: str, code: str):
        full_path = os.path.join(self.base_dir, filepath)
        with open(full_path, "a") as f:
            f.write("\n" + code)
        self._log(filepath, "appended")

    def _log(self, filepath, action):
        try:
            conn = sqlite3.connect(self.audit_log)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (timestamp, agent, action, context)
                VALUES (?, ?, ?, ?)
            """, (datetime.utcnow(), "ATOM", f"File {action}", filepath))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Audit log failed:", e)
