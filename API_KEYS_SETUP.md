# API Keys & Credentials Setup Guide

## Overview
AI Revenue Command Center requires several API keys and credentials for full functionality. This guide will help you set them up properly.

## Required API Keys

### 1. Stripe (Payment Processing)
**Purpose**: Handle real payment processing and revenue generation
**Required for**: Product sales, customer payments, automated payouts

**Setup Steps**:
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Create account or log in
3. Get your API keys from Developers → API Keys
4. Copy the **Secret Key** (starts with `sk_test_` or `sk_live_`)

### 2. Local LLM (Ollama)
**Purpose**: Power AI agent decision making and analysis without hosted APIs
**Required for**: Autonomous operations, market research, strategic planning

**Setup Steps**:
1. Download and install [Ollama](https://ollama.ai/download)
2. Start the Ollama service (`ollama serve` runs automatically after install)
3. Pull a model: `ollama pull llama3.1:8b`
4. (Optional) Pull additional models for specialized workflows
5. Verify the API responds at `http://localhost:11434`

> Optional hosted alternatives: You can still configure `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` if you prefer paid providers.

### 3. Email Service (Communications)
**Purpose**: Send automated emails, newsletters, customer communications
**Required for**: Marketing campaigns, customer notifications, sales follow-ups

**Setup Steps**:
1. Use Gmail, Outlook, or any SMTP provider
2. Get SMTP credentials:
   - **SMTP Server**: smtp.gmail.com (for Gmail)
   - **Port**: 587
   - **Email**: your-email@gmail.com
   - **Password**: Your email password or app password

### 4. Twitter/X API (Social Media Marketing)
**Purpose**: Automated social media posting and engagement
**Required for**: Marketing campaigns, brand awareness, lead generation

**Setup Steps**:
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create developer account
3. Create new app/project
4. Get API credentials:
   - API Key
   - API Key Secret
   - Access Token
   - Access Token Secret

### 5. LinkedIn API (Professional Networking)
**Purpose**: B2B marketing and professional networking
**Required for**: Business development, partnership outreach

**Setup Steps**:
1. Go to [LinkedIn Developers](https://developer.linkedin.com/)
2. Create developer account
3. Create new app
4. Get Client ID and Client Secret

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# LLM Configuration (local default)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Remote providers (uncomment if you plan to pay for hosted APIs)
# OPENAI_API_KEY=sk-your_openai_api_key_here
# ANTHROPIC_API_KEY=sk-your_anthropic_api_key_here
# LLM_PROVIDER=openai  # or anthropic

# Email Configuration
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-email-password-or-app-password

# Twitter Configuration
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_token_secret

# LinkedIn Configuration
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
```

### Method 2: System Environment Variables

#### Windows (Command Prompt):
```cmd
set STRIPE_SECRET_KEY=sk_test_your_key_here
set LLM_PROVIDER=ollama
set LLM_MODEL=llama3.1:8b
set OLLAMA_BASE_URL=http://localhost:11434
set SMTP_EMAIL=your-email@gmail.com
set SMTP_PASSWORD=your-password
```

#### Windows (PowerShell):
```powershell
$env:STRIPE_SECRET_KEY = "sk_test_your_key_here"
$env:LLM_PROVIDER = "ollama"
$env:LLM_MODEL = "llama3.1:8b"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:SMTP_EMAIL = "your-email@gmail.com"
$env:SMTP_PASSWORD = "your-password"
```

#### Linux/Mac:
```bash
export STRIPE_SECRET_KEY=sk_test_your_key_here
export LLM_PROVIDER=ollama
export LLM_MODEL=llama3.1:8b
export OLLAMA_BASE_URL=http://localhost:11434
export SMTP_EMAIL=your-email@gmail.com
export SMTP_PASSWORD=your-password
```

### Method 3: Python Script Setup

Create `setup_credentials.py`:

```python
import os

# Set your API keys here
credentials = {
    'STRIPE_SECRET_KEY': 'sk_test_your_stripe_key',
    'LLM_PROVIDER': 'ollama',
    'LLM_MODEL': 'llama3.1:8b',
    'OLLAMA_BASE_URL': 'http://localhost:11434',
    'SMTP_EMAIL': 'your-email@gmail.com',
    'SMTP_PASSWORD': 'your-password',
    'TWITTER_API_KEY': 'your_twitter_key',
    'TWITTER_API_SECRET': 'your_twitter_secret',
    'TWITTER_ACCESS_TOKEN': 'your_access_token',
    'TWITTER_ACCESS_SECRET': 'your_access_secret',
}

# Set environment variables
for key, value in credentials.items():
    os.environ[key] = value
    print(f"Set {key}")

print("All credentials configured!")
```

## Testing Configuration

After setting up credentials, restart the server and check the logs. You should see:

- ✅ Stripe API key configured (if using Stripe)
- ✅ LLM provider configured (Ollama by default)
- ✅ Email credentials configured (if using SMTP)
- ✅ Twitter API credentials configured (if enabled)

Instead of warning messages such as:
- ⚠️ Stripe API key not found
- ⚠️ LLM provider not reachable
- ⚠️ SMTP credentials not found

## Security Best Practices

1. **Never commit API keys to version control**
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Use restricted access**
   - Stripe: Use test keys for development
   - LLM Provider: Limit network exposure (bind Ollama to localhost)
   - Twitter: Use read/write permissions only as needed

3. **Rotate keys regularly**
   - Change keys every 3-6 months
   - Monitor usage for suspicious activity

4. **Environment separation**
   - Use different keys for development/staging/production
   - Test with limited permissions first

## Troubleshooting

### Common Issues

1. **"API key not found" warnings persist**
   - Ensure environment variables are set correctly
   - Restart the server after setting variables
   - Check variable names match exactly

2. **Stripe test payments not working**
   - Verify you're using test keys (start with `sk_test_`)
   - Check webhook endpoints are configured

3. **LLM service errors**
   - Confirm Ollama service is running (`ollama list`)
   - Ensure the model has been pulled successfully
   - Verify `LLM_PROVIDER`/`OLLAMA_BASE_URL` environment variables

4. **Email sending fails**
   - Verify SMTP credentials
   - Check if 2FA is enabled (use app passwords)
   - Test with a simple email first

### Verification Commands

Test your setup with these curl commands:

```bash
# Test Stripe configuration
curl http://localhost:8080/api/stripe/status

# Test system status
curl http://localhost:8080/api/system_status

# Test AI functionality
curl http://localhost:8080/api/market_research
```

## Next Steps

1. Set up all required API keys
2. Restart the server
3. Verify configuration in logs
4. Test key functionality
5. Begin autonomous operations

## Support

If you encounter issues:
1. Check the server logs for error messages
2. Verify API key formats and permissions
3. Test with minimal configuration first
4. Contact API provider support if needed

---

*Secure API key management is crucial for system security and functionality.*
