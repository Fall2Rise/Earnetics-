# Stripe Operations Runbook

## Emergency Procedures

### Webhook Delivery Failures

**Symptoms:**
- High retry rate in Stripe Dashboard
- Non-2xx responses from webhook endpoint
- Missing fulfillment events

**Actions:**
1. Check webhook endpoint health: `GET /api/stripe/webhook/health`
2. Review recent webhook logs: `GET /api/stripe/webhook/logs`
3. Verify signature secret matches Stripe Dashboard
4. Check server logs for errors
5. If persistent, manually replay failed events from Stripe Dashboard

### Payment Processing Failures

**Symptoms:**
- Spike in `payment_intent.payment_failed` events
- Customer complaints about failed payments

**Actions:**
1. Check payment method decline reasons in Stripe Dashboard
2. Review fraud detection settings
3. Verify card validation rules
4. Check for API rate limits
5. Review customer payment history

### Dispute Handling

**Symptoms:**
- `charge.dispute.created` events
- Dispute notifications from Stripe

**Actions:**
1. Gather evidence within 7 days (Stripe deadline)
2. Submit evidence via Stripe Dashboard or API
3. Log dispute in audit trail
4. Update customer record if needed
5. Monitor `charge.dispute.closed` for resolution

### Refund Processing

**Symptoms:**
- High refund volume
- Customer refund requests

**Actions:**
1. Verify refund eligibility (policy check)
2. Process refund via Stripe API
3. Revoke access immediately upon refund
4. Update ledger and customer records
5. Notify customer of refund completion

## Routine Maintenance

### Daily Checks
- [ ] Review webhook delivery health
- [ ] Check for failed payments spike
- [ ] Monitor dispute activity
- [ ] Review refund volume
- [ ] Check subscription churn rate

### Weekly Tasks
- [ ] Generate weekly health report
- [ ] Review and update runbooks
- [ ] Audit webhook event subscriptions
- [ ] Check for unused products/prices
- [ ] Review API key permissions

### Monthly Tasks
- [ ] Full security audit
- [ ] Review and rotate API keys (if needed)
- [ ] Update documentation
- [ ] Review compliance settings
- [ ] Performance optimization review

## Configuration Changes

### Adding New Webhook Events

1. **Propose Change:**
   - Document event purpose
   - Identify handler location
   - Define idempotency strategy
   - Create rollback plan

2. **If AUTO_APPLY_CHANGES=false:**
   - Submit change proposal
   - Wait for approval
   - Apply change manually

3. **If AUTO_APPLY_CHANGES=true:**
   - Apply change
   - Log change in CHANGELOG.md
   - Monitor for 24 hours
   - Verify no regressions

### Modifying Products/Prices

**Before:**
- Document current state
- Create backup
- Define rollback plan

**During:**
- Make changes in test mode first
- Verify changes
- Apply to live if approved

**After:**
- Update documentation
- Log in CHANGELOG.md
- Monitor for issues

## Monitoring Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Webhook failure rate | >2% | >5% | Investigate endpoint |
| Payment failure rate | >10% | >20% | Review payment methods |
| Dispute rate | >1% | >3% | Review fraud settings |
| Refund rate | >5% | >10% | Review product quality |
| Subscription churn | >5%/month | >10%/month | Review retention |

## Alert Targets

- **Slack**: `#stripe-ops-alerts`
- **Email**: `stripe-ops@earnetics.live`
- **Webhook**: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`

## Contact Information

- **Stripe Support**: https://support.stripe.com
- **Internal Escalation**: Contact Vega (CFO) or Atlas (COO)

