import os

def restore_keys():
    backup_path = ".env.backup"
    current_path = ".env"
    
    backup_lines = []
    if os.path.exists(backup_path):
        with open(backup_path, "r") as f:
            backup_lines = f.readlines()
    else:
        print("❌ No backup found!")
        return

    current_lines = []
    if os.path.exists(current_path):
        with open(current_path, "r") as f:
            current_lines = f.readlines()

    # Parse backup into dict
    backup_keys = {}
    for line in backup_lines:
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            backup_keys[k.strip()] = v.strip()

    # Parse current into dict
    current_keys = {}
    for line in current_lines:
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            current_keys[k.strip()] = v.strip()

    # Merge: If missing in current, take from backup
    restored_count = 0
    for k, v in backup_keys.items():
        if k not in current_keys:
            print(f"♻️  Restoring {k}...")
            current_keys[k] = v
            restored_count += 1
        elif current_keys[k] == "" or current_keys[k] == "MISSING": # If empty in current but present in backup
             print(f"♻️  Restoring empty {k} from backup...")
             current_keys[k] = v
             restored_count += 1

    # Write back to .env
    with open(current_path, "w") as f:
        for k, v in current_keys.items():
            f.write(f"{k}={v}\n")
    
    print(f"✅ Restored {restored_count} keys from backup.")
    
    # Verify critical keys
    print("\n--- Current Critical Keys ---")
    for key in ["GOOGLE_API_KEY", "OPENROUTER_API_KEY", "SMTP_PASSWORD"]:
        val = current_keys.get(key, "MISSING")
        masked = "*" * 10 if len(val) > 5 else val
        print(f"{key}: {masked}")

if __name__ == "__main__":
    restore_keys()
