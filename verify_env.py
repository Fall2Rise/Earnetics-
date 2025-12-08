import os
try:
    # Try reading as utf-8 first
    with open(".env", "r", encoding="utf-8") as f:
        lines = f.readlines()
except UnicodeDecodeError:
    # Fallback to utf-16 if utf-8 fails (PowerShell Set-Content default)
    with open(".env", "r", encoding="utf-16") as f:
        lines = f.readlines()
except Exception as e:
    with open("env_verification.txt", "w") as out:
        out.write(f"Error opening .env: {e}")
    exit(1)

with open("env_verification.txt", "w", encoding="utf-8") as out:
    found = False
    for line in lines:
        if "STRIPE_SECRET_KEY" in line:
            out.write(f"Found key line: {line.strip()}\n")
            found = True
    if not found:
        out.write("STRIPE_SECRET_KEY not found in .env\n")
