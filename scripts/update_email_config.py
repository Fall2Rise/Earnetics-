#!/usr/bin/env python3
"""Update email configuration with new credentials."""

import os

# Read current .env
with open('.env', 'r') as f:
    lines = f.readlines()

# Update SMTP settings
new_lines = []
email_updated = False
password_updated = False

for line in lines:
    if line.strip().startswith('SMTP_EMAIL='):
        new_lines.append('SMTP_EMAIL=selfbuilddigital@gmail.com\n')
        email_updated = True
        print("✅ Updated SMTP_EMAIL to: selfbuilddigital@gmail.com")
    elif line.strip().startswith('SMTP_PASSWORD='):
        # Remove spaces from password
        clean_password = 'itckthzdahrjnjfx'
        new_lines.append(f'SMTP_PASSWORD={clean_password}\n')
        password_updated = True
        print(f"✅ Updated SMTP_PASSWORD to: {clean_password}")
    else:
        new_lines.append(line)

# Write back
with open('.env', 'w') as f:
    f.writelines(new_lines)

print("\n✅ Email configuration updated!")
print("   Email: selfbuilddigital@gmail.com")
print("   Password: itckthzdahrjnjfx")
