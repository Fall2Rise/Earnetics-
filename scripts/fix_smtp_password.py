#!/usr/bin/env python3
"""Fix SMTP password by removing spaces."""

import os

# Read current .env
with open('.env', 'r') as f:
    lines = f.readlines()

# Fix SMTP_PASSWORD
new_lines = []
for line in lines:
    if line.strip().startswith('SMTP_PASSWORD='):
        # Remove spaces from the password
        old_password = line.split('=', 1)[1].strip()
        new_password = old_password.replace(' ', '')
        new_lines.append(f'SMTP_PASSWORD={new_password}\n')
        print(f"Fixed password: '{old_password}' -> '{new_password}'")
    else:
        new_lines.append(line)

# Write back
with open('.env', 'w') as f:
    f.writelines(new_lines)

print("✅ SMTP password spaces removed!")
print("\nNow test with: python scripts\\debug_email.py")
