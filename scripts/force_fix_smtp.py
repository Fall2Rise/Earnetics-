#!/usr/bin/env python3
"""Force fix SMTP password - remove all spaces."""

# Read the .env file
with open('.env', 'r') as f:
    content = f.read()

# Fix the SMTP password line specifically
lines = content.split('\n')
new_lines = []

for line in lines:
    if line.startswith('SMTP_PASSWORD='):
        # Extract password and remove ALL spaces
        password_part = line.split('=', 1)[1]
        clean_password = password_part.replace(' ', '').strip()
        new_lines.append(f'SMTP_PASSWORD={clean_password}')
        print(f"✅ Fixed: SMTP_PASSWORD={clean_password}")
    else:
        new_lines.append(line)

# Write back
with open('.env', 'w') as f:
    f.write('\n'.join(new_lines))

print("\n✅ SMTP password fixed!")
print("Password is now: outvrmlsextqmhlc (no spaces)")
