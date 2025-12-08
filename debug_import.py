import sys
import os

print("Python executable:", sys.executable)
print("CWD:", os.getcwd())
print("Path:", sys.path)

try:
    print("Attempting to import ai_corporation_agents...")
    import ai_corporation_agents
    print("Import successful!")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
