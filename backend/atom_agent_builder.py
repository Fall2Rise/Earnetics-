import os
from datetime import datetime
import sqlite3

class AtomAgentBuilder:
    def __init__(self, agent_dir="backend/agents", registry_file="backend/ai_corporation_agents.py", vector_db="vector_memory.db", audit_log="audit_log.db"):
        self.agent_dir = agent_dir
        self.registry_file = registry_file
        self.vector_db = vector_db
        self.audit_log = audit_log

    def create_agent(self, agent_name, agent_role, agent_purpose):
        class_name = agent_name.replace(" ", "").replace("_", "") + "Agent"
        filename = f"{agent_name.lower()}.py"
        file_path = os.path.join(self.agent_dir, filename)

        code = f"""class {class_name}:
    def __init__(self):
        self.name = "{agent_name}"
        self.role = "{agent_role}"
        self.purpose = "{agent_purpose}"
        self.extensions = {{}}

    def execute(self):
        print("Executing {agent_name} operations...")

    def extend(self, function_name: str, function_code: str):
        try:
            exec(function_code, globals())
            self.extensions[function_name] = eval(function_name)
            setattr(self, function_name, eval(function_name))
            print(f"Extended agent with: {{function_name}}")
        except Exception as e:
            print(f"Extension failed: {{e}}")
"""

        os.makedirs(self.agent_dir, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(code)

        self._register_agent(agent_name, filename, class_name)
        self._log_creation(agent_name, agent_purpose)
        self._store_vector(agent_name, agent_purpose)
        return {
            "status": "Agent created",
            "file": file_path,
            "class": class_name
        }

    def _register_agent(self, name, filename, class_name):
        with open(self.registry_file, "a") as f:
            f.write(f"\nfrom backend.agents.{filename.replace('.py','')} import {class_name}")
            f.write(f"\nagents['{name}'] = {class_name}()")

    def _log_creation(self, name, purpose):
        conn = sqlite3.connect(self.audit_log)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (timestamp, agent, action, context)
            VALUES (?, ?, ?, ?)
        """, (datetime.utcnow(), "ATOM_AGENT_BUILDER", "agent_created", f"{name}: {purpose}"))
        conn.commit()
        conn.close()

    def _store_vector(self, name, purpose):
        conn = sqlite3.connect(self.vector_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vectors (title, content, tag)
            VALUES (?, ?, ?)
        """, (name, purpose, "agent_blueprint"))
        conn.commit()
        conn.close()
