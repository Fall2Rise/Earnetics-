import os
from datetime import datetime
import sqlite3
import shutil

class AtomCloningEngine:
    def __init__(self, agents_dir="backend/agents", registry_file="backend/ai_corporation_agents.py", vector_db="vector_memory.db", audit_log="audit_log.db"):
        self.agents_dir = agents_dir
        self.registry_file = registry_file
        self.vector_db = vector_db
        self.audit_log = audit_log

    def clone_agent(self, base_agent_name, new_agent_name, custom_directive):
        src_file = os.path.join(self.agents_dir, f"{base_agent_name.lower()}.py")
        dest_file = os.path.join(self.agents_dir, f"{new_agent_name.lower()}.py")

        if not os.path.exists(src_file):
            return {"status": "error", "message": f"{base_agent_name}.py not found."}

        shutil.copy(src_file, dest_file)

        self._inject_directive(dest_file, custom_directive)
        self._register_clone(new_agent_name, dest_file)
        self._log_clone(new_agent_name, custom_directive)

        return {
            "status": "success",
            "message": f"{new_agent_name} created from {base_agent_name}.",
            "directive": custom_directive
        }

    def _inject_directive(self, file_path, directive):
        with open(file_path, "a") as f:
            f.write(f"\n# Injected directive: {directive}\n")
            f.write(f"    def directive(self):\n        print('{directive}')\n")

    def _register_clone(self, name, file_path):
        class_name = name.replace(" ", "") + "Agent"
        module_name = file_path.split("/")[-1].replace(".py", "")
        with open(self.registry_file, "a") as f:
            f.write(f"\nfrom backend.agents.{module_name} import {class_name}")
            f.write(f"\nagents['{name}'] = {class_name}()")

    def _log_clone(self, name, directive):
        conn = sqlite3.connect(self.audit_log)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (timestamp, agent, action, context)
            VALUES (?, ?, ?, ?)
        """, (datetime.utcnow(), "ATOM_CLONER", "CLONED_AGENT", f"{name} with directive: {directive}"))
        conn.commit()
        conn.close()
