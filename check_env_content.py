import os
import sys

def check_file(path, out_file):
    out_file.write(f"Checking {path}...\n")
    if not os.path.exists(path):
        out_file.write("File not found.\n")
        return

    try:
        with open(path, 'rb') as f:
            content = f.read()
        
        out_file.write(f"Size: {len(content)} bytes\n")
        try:
            text = content.decode('utf-8')
            out_file.write("Encoding: utf-8\n")
        except UnicodeDecodeError:
            try:
                text = content.decode('utf-16le')
                out_file.write("Encoding: utf-16le\n")
            except UnicodeDecodeError:
                out_file.write("Encoding: unknown binary\n")
                return

        lines = text.splitlines()
        out_file.write(f"Total lines: {len(lines)}\n")
        out_file.write("First 5 lines:\n")
        for line in lines[:5]:
            out_file.write(f"{line}\n")
            
        out_file.write("\nChecking for specific keys...\n")
        keys_to_check = ["OPENAI_API_KEY", "STRIPE_SECRET_KEY", "ANTHROPIC_API_KEY", "PRIME_DIRECTIVE_HMAC_SECRET"]
        for key in keys_to_check:
            found = any(key in line for line in lines)
            out_file.write(f"{key}: {'FOUND' if found else 'MISSING'}\n")

    except Exception as e:
        out_file.write(f"Error reading file: {e}\n")

with open('env_check_result.txt', 'w', encoding='utf-8') as f:
    f.write("--- .env ---\n")
    check_file(".env", f)
    f.write("\n--- .env.backup ---\n")
    check_file(".env.backup", f)
