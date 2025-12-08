import sys
import traceback
import os

log_file = "server_debug_log.md"

def log(msg):
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except:
        pass

# Clear file
with open(log_file, "w", encoding="utf-8") as f:
    f.write("--- SERVER DEBUG LOG v9 ---\n")

log(f"CWD: {os.getcwd()}")
sys.path.insert(0, os.getcwd())

try:
    log("Importing sentence_transformers...")
    from sentence_transformers import SentenceTransformer
    log("Imported sentence_transformers")
    
except Exception:
    log("\n❌ EXCEPTION OCCURRED:")
    log(traceback.format_exc())
except SystemExit as e:
    log(f"\n❌ SystemExit: {e}")
finally:
    log("--- END LOG ---")
