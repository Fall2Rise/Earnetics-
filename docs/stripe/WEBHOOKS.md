# Stripe Webhooks Configuration

## Overview
This document describes the webhook endpoints, event subscriptions, and delivery configuration for Earnetics' Stripe integration.

## Webhook Endpoints

### Production
- **URL**: `https://www.fallat.digital/api/stripe/webhook`
- **Environment**: Live
- **Status**: Active

### Test
- **URL**: `http://localhost:8000/api/stripe/webhook` (development)
- **Environment**: Test
- **Status**: Active (development only)

## Event Subscriptions

### Minimal Safe Event Set

#### One-Time Payments
- `payment_intent.succeeded` - Primary fulfillment trigger
- `payment_intent.payment_failed` - Failure handling
- `checkout.session.completed` - Order record creation (optional)

#### Subscriptions
- `invoice.paid` - Primary fulfillment trigger
- `invoice.payment_failed` - Failure handling
- `customer.subscription.updated` - Access state changes
- `customer.subscription.deleted` - Cancellation handling
- `customer.subscription.created` - New subscription tracking (optional)

#### Disputes & Refunds
- `charge.refunded` - Refund processing
- `charge.dispute.created` - Dispute notification
- `charge.dispute.closed` - Dispute resolution

#### Connect (if enabled)
- `transfer.created` - Transfer confirmation
- `transfer.reversed` - Transfer reversal
- `transfer.canceled` - Transfer cancellation

## Signature Verification

All webhook handlers MUST verify Stripe signatures using the raw request body.

```python
import stripe

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    try:
        stripe.Webhook.construct_event(payload, signature, secret)
        return True
    except ValueError:
        return False
```

## Event Deduplication

Events are deduplicated by `event.id` to prevent double-processing.

## Idempotency

All fulfillment operations are keyed by:
- One-time: `payment_intent.id`
- Subscriptions: `invoice.id`

## Monitoring

- Delivery failures tracked in Stripe Dashboard
- Retry rate monitored via webhook logs
- Alert thresholds: >5% failure rate, >3 retries per event

## Change Log

See [CHANGELOG.md](./CHANGELOG.md) for webhook configuration changes.

