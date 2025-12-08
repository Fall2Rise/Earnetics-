#!/usr/bin/env python3
"""Update Google API key in .env file."""

import os

# Read current .env
with open('.env', 'r') as f:
    lines = f.readlines()

# Update or add GOOGLE_API_KEY
new_lines = []
key_found = False

for line in lines:
    if line.strip().startswith('GOOGLE_API_KEY='):
        new_lines.append('GOOGLE_API_KEY=e15f3f37b29361f903f012831f1b7f5648d3f55a\n')
        key_found = True
    else:
        new_lines.append(line)

# If key wasn't found, add it
if not key_found:
    new_lines.append('\nGOOGLE_API_KEY=e15f3f37b29361f903f012831f1b7f5648d3f55a\n')

# Write back
with open('.env', 'w') as f:
    f.writelines(new_lines)

print("✅ Google API Key updated successfully!")
