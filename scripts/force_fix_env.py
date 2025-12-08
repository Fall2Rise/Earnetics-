import os

def fix_env():
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    keys_to_check = {
        "GOOGLE_API_KEY": "AIzaSyBaHP6VLW0bTuizsFbDGQ6Ts9H9ez0ki98",
        "OPENROUTER_API_KEY": "sk-or-v1-...", # I don't have the full key, so I won't overwrite if it exists but is just not loading due to formatting.
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_EMAIL": "fallataienterprises@gmail.com",
        # "SMTP_PASSWORD": "..." # I won't hardcode this if I don't have to
    }

    new_lines = []
    seen_keys = set()
    
    print("--- Current .env content (sanitized) ---")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            new_lines.append(line)
            continue
        
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            seen_keys.add(key)
            
            # Fix common issues
            if key in ["GOOGLE_API_KEY", "OPENROUTER_API_KEY", "SMTP_PASSWORD"]:
                # Ensure no quotes if they are causing issues, or proper quotes
                # For now, let's just print what we see
                print(f"Found {key}: {val[:5]}...")
            
            new_lines.append(f"{key}={val}")
    
    # Add missing keys if I have them
    if "GOOGLE_API_KEY" not in seen_keys:
        print("Adding missing GOOGLE_API_KEY")
        new_lines.append(f"GOOGLE_API_KEY={keys_to_check['GOOGLE_API_KEY']}")
    
    # Write back
    with open(".env", "w") as f:
        f.write("\n".join(new_lines))
    
    print("--- .env fixed ---")

if __name__ == "__main__":
    fix_env()
