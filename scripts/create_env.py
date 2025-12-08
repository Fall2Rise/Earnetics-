
content = """# --- AI REVENUE COMMAND CENTER CONFIG ---

# 1. INTELLIGENCE (The Brain)
GOOGLE_API_KEY=AIzaSyBaHP6VLW0bTuizsFbDGQ6Ts9H9ez0ki98
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE

# 2. PAYMENTS (The Bank)
STRIPE_SECRET_KEY=sk_live_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY_HERE

# 3. OUTREACH (Email)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=selfbuilddigital@gmail.com
SMTP_PASSWORD=YOUR_APP_PASSWORD_HERE

# 4. SYSTEM
LOG_LEVEL=INFO
AUTONOMY_WORKER_ENABLED=true
"""

with open(".env", "w") as f:
    f.write(content)

print("✅ .env file created successfully.")
