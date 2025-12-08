import os

search_dirs = [".venv", "venv"]
print("Searching recursively for STRIPE_SECRET_KEY in .venv/venv...")

with open("key_search_result.txt", "w") as out:
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
            
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                # Check .env files or any file that might be a config
                if file == ".env" or file.endswith(".env") or file == "config.py":
                    path = os.path.join(root, file)
                    try:
                        content = open(path, "r", encoding="utf-8", errors="ignore").read()
                        if "STRIPE_SECRET_KEY" in content:
                            out.write(f"FOUND IN: {path}\n")
                            if "sk_live_" in content:
                                out.write(f"  -> Has Live Key format (sk_live_...)\n")
                            else:
                                out.write(f"  -> Key format unrecognized or placeholder\n")
                    except Exception:
                        pass
