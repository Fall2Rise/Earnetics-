import os
from dotenv import load_dotenv

# Read current .env
with open('.env', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Keys to add
google_key = "GOOGLE_API_KEY=AIzaSyBaHP6VLW0bTuizsFbDGQ6Ts9H9ez0ki98"
openrouter_key = "OPENROUTER_API_KEY=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"

# Check if keys exist
has_google = any('GOOGLE_API_KEY=' in line for line in lines)
has_openrouter = any('OPENROUTER_API_KEY=' in line for line in lines)

new_lines = []
for line in lines:
    # Fix SMTP password if it has spaces
    if 'SMTP_PASSWORD=' in line and 'outv rlms' in line:
        new_lines.append('SMTP_PASSWORD=outvrlmsextqmhlc\n')
    # Update Google key if it exists
    elif 'GOOGLE_API_KEY=' in line:
        new_lines.append(google_key + '\n')
        has_google = False  # Mark as handled
    # Update OpenRouter key if it exists
    elif 'OPENROUTER_API_KEY=' in line:
        new_lines.append(openrouter_key + '\n')
        has_openrouter = False  # Mark as handled
    else:
        new_lines.append(line)

# Add missing keys at the end
if has_google:
    new_lines.append(google_key + '\n')
if has_openrouter:
    new_lines.append(openrouter_key + '\n')

# Write back
with open('.env', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Verify
load_dotenv(override=True)
print("✅ GOOGLE_API_KEY:", "SET" if os.getenv('GOOGLE_API_KEY') else "MISSING")
print("✅ OPENROUTER_API_KEY:", "SET" if os.getenv('OPENROUTER_API_KEY') else "MISSING")
print("✅ SMTP_PASSWORD:", "16 chars" if os.getenv('SMTP_PASSWORD') and len(os.getenv('SMTP_PASSWORD')) == 16 else "ISSUE")
