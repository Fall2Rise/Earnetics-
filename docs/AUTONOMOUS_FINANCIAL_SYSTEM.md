# Autonomous Financial System - 80/20 Revenue Split

## Overview

This system automatically processes all revenue through an 80/20 split:
- **80% to you** (owner) - Automatically paid out to your bank account via Stripe
- **20% reinvested** - Automatically allocated to business operations, marketing, and growth

## Features

### ✅ Implemented

1. **Automatic Revenue Processing**
   - Monitors all incoming transactions
   - Automatically calculates 80/20 split
   - Records all financial operations in database

2. **Real Stripe Payouts**
   - Creates actual Stripe payouts to your connected bank account
   - Tracks payout status (pending, in_transit, paid, failed)
   - Batches small payouts to minimize fees
   - Handles errors gracefully with retry logic

3. **Reinvestment Management**
   - Automatically allocates 20% to reinvestment fund
   - Makes intelligent decisions on fund allocation:
     - Infrastructure (API credits, hosting)
     - Marketing campaigns
     - Product development
   - Tracks spending and remaining balances

4. **Continuous Monitoring**
   - Runs 24/7 without human intervention
   - Syncs payout statuses every 5 minutes
   - Processes new transactions every minute
   - Makes reinvestment decisions every hour
   - Reports financial health metrics

5. **Error Handling**
   - Queues payouts if Stripe isn't configured
   - Handles insufficient funds gracefully
   - Records all failures for review
   - Auto-recovers from temporary errors

## Setup Instructions

### 1. Stripe Configuration

You need a Stripe account with payouts enabled:

1. **Create Stripe Account**: https://dashboard.stripe.com/register
2. **Complete Account Setup**: 
   - Add business information
   - Connect your bank account
   - Verify your identity
3. **Enable Payouts**: Ensure "Payouts" are enabled in your Stripe dashboard
4. **Get API Keys**: Dashboard → Developers → API keys

### 2. Environment Variables

Create a `.env` file in the project root:

```bash
# Required for payouts
STRIPE_SECRET_KEY=sk_test_...  # Use sk_live_... for production

# Optional but recommended
STRIPE_WEBHOOK_SECRET=whsec_...  # For webhook verification
OPENAI_API_KEY=sk-...  # For AI agents (or use Ollama)

# Optional email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Database Setup

The system automatically creates all necessary tables:
- `financial_operations` - Tracks all 80/20 splits
- `stripe_payouts` - Tracks payout status
- `reinvestment_operations` - Tracks reinvestment allocations
- `transactions` - Source transactions

### 4. Start the System

```bash
# Start the autonomous financial processor
python backend/start_autonomous_system.py
```

The system will:
1. Check your environment configuration
2. Initialize Stripe connection
3. Start processing revenue automatically
4. Begin making payouts and reinvestment decisions

## How It Works

### Revenue Flow

```
Incoming Transaction ($100)
         ↓
    80/20 Split
    ↙         ↘
$80 Owner    $20 Reinvest
    ↓             ↓
Stripe Payout   Allocation:
to Bank         - Infrastructure
Account         - Marketing
                - Product Dev
```

### Payout Logic

1. **Immediate Payouts** (≥ $10): Processed immediately
2. **Batched Payouts** (< $10): Combined hourly to reduce fees
3. **Status Tracking**: 
   - `pending` → `in_transit` → `paid`
   - Synced with Stripe every 5 minutes

### Reinvestment Decisions

The system automatically allocates the 20% reinvestment fund:

1. **Infrastructure (40%)**: API credits, hosting, tools
2. **Marketing (30%)**: Automated campaigns, ads
3. **Product (30%)**: New features, improvements

## Monitoring

### Logs

All activity is logged to:
- `logs/autonomous_system.log` - Main system log
- `logs/operational_system.log` - Operational events
- Console output - Real-time status

### Financial Health Metrics

Logged every hour:
- Total revenue processed
- Total paid out to owner
- Total reinvested
- Pending payout amount
- Failed payout count

### Example Log Output

```
2024-01-15 10:30:00 - AutonomousFinancial - INFO - 💰 Processed transaction #123: $100.00 → Owner: $80.00, Reinvest: $20.00
2024-01-15 10:30:01 - AutonomousFinancial - INFO - ✅ Payout initiated: $80.00 (ID: po_1234567890)
2024-01-15 10:30:02 - AutonomousFinancial - INFO - 💡 Reinvestment decision: $20.00 → infrastructure (API credits and hosting)
2024-01-15 11:00:00 - AutonomousFinancial - INFO - 📊 Financial Health: Total Revenue: $1,250.00, Paid Out: $1,000.00, Reinvested: $250.00, Pending: $0.00
```

## Testing

### Test Mode (Recommended First)

Use Stripe test keys to verify everything works:

```bash
STRIPE_SECRET_KEY=sk_test_...  # Test key
```

Test payouts will show in your Stripe dashboard but won't transfer real money.

### Create Test Transaction

```python
from backend.autonomous_financial_processor import AutonomousFinancialProcessor

processor = AutonomousFinancialProcessor()

# Simulate a $100 transaction
# This will automatically:
# 1. Split 80/20
# 2. Queue $80 payout
# 3. Allocate $20 to reinvestment
```

## Production Deployment

### 1. Switch to Live Keys

```bash
STRIPE_SECRET_KEY=sk_live_...  # Live key
```

### 2. Run as Background Service

**Using systemd (Linux):**

Create `/etc/systemd/system/fallat-autonomous.service`:

```ini
[Unit]
Description=Fallat Autonomous Financial System
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Fallat_CrewAI
Environment="STRIPE_SECRET_KEY=sk_live_..."
ExecStart=/usr/bin/python3 backend/start_autonomous_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fallat-autonomous
sudo systemctl start fallat-autonomous
sudo systemctl status fallat-autonomous
```

**Using Docker:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENV STRIPE_SECRET_KEY=sk_live_...

CMD ["python", "backend/start_autonomous_system.py"]
```

Build and run:
```bash
docker build -t fallat-autonomous .
docker run -d --restart=always fallat-autonomous
```

### 3. Monitor Production

- Check logs regularly: `tail -f logs/autonomous_system.log`
- Monitor Stripe dashboard for payout status
- Set up alerts for failed payouts
- Review financial health metrics

## Troubleshooting

### Payouts Not Working

1. **Check Stripe Configuration**:
   ```python
   from backend.stripe_integration import StripePaymentProcessor
   processor = StripePaymentProcessor()
   result = processor.configure_from_environment()
   print(result)
   ```

2. **Verify Payouts Enabled**: 
   - Go to Stripe Dashboard
   - Check if payouts are enabled
   - Ensure bank account is connected

3. **Check Balance**:
   ```python
   balance = processor.get_stripe_balance()
   print(balance)
   ```

### Payouts Queued as "pending_config"

- Stripe API key not set or invalid
- Set `STRIPE_SECRET_KEY` environment variable
- Restart the system

### Payouts Failing

- Insufficient Stripe balance
- Bank account not verified
- Check `stripe_payouts` table for `failure_reason`

### System Not Processing Transactions

- Check if transactions have `status = 'completed'`
- Verify database connection
- Check logs for errors

## Security Notes

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Restrict API key permissions** in Stripe dashboard
4. **Enable webhook signature verification** for production
5. **Monitor for suspicious activity** in logs

## Next Steps

After the financial system is running:

1. ✅ **Revenue is flowing automatically** - 80% to you, 20% reinvested
2. 🔄 **Next: Autonomous Revenue Generation** - Build systems that create revenue
3. 🤖 **Next: Agent Learning** - Make agents smarter over time
4. 📈 **Next: Scale Operations** - Multiple revenue streams

## Support

For issues or questions:
1. Check logs: `logs/autonomous_system.log`
2. Review Stripe dashboard
3. Check database: `sqlite3 financial/corporate_operations.db`

---

**Status**: ✅ Fully Implemented and Ready for Production

The autonomous financial system is now complete and will automatically:
- Process all revenue through 80/20 split
- Pay you via Stripe to your bank account
- Reinvest 20% into business operations
- Run 24/7 without human intervention
