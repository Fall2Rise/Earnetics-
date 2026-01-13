# Stripe Events Mapping

## Event → Action Mapping

This document maps Stripe webhook events to Earnetics system actions.

### Payment Events

| Event | Trigger | Action | Idempotency Key |
|-------|---------|--------|-----------------|
| `payment_intent.succeeded` | Money confirmed | Fulfill order, grant access | `payment_intent.id` |
| `payment_intent.payment_failed` | Payment failed | Log failure, notify customer | `payment_intent.id` |
| `checkout.session.completed` | Checkout finished | Create order record (no fulfillment) | `checkout_session.id` |

### Subscription Events

| Event | Trigger | Action | Idempotency Key |
|-------|---------|--------|-----------------|
| `invoice.paid` | Subscription payment confirmed | Grant/refresh access | `invoice.id` |
| `invoice.payment_failed` | Subscription payment failed | Log failure, handle retry | `invoice.id` |
| `customer.subscription.updated` | Subscription changed | Update access state | `subscription.id` |
| `customer.subscription.deleted` | Subscription canceled | Revoke access | `subscription.id` |
| `customer.subscription.created` | New subscription | Track subscription start | `subscription.id` |

### Dispute & Refund Events

| Event | Trigger | Action | Idempotency Key |
|-------|---------|--------|-----------------|
| `charge.refunded` | Refund processed | Revoke access, update ledger | `charge.id` |
| `charge.dispute.created` | Dispute opened | Alert operations, gather evidence | `dispute.id` |
| `charge.dispute.closed` | Dispute resolved | Update records, handle outcome | `dispute.id` |

### Connect Events (if enabled)

| Event | Trigger | Action | Idempotency Key |
|-------|---------|--------|-----------------|
| `transfer.created` | Transfer initiated | Log transfer, update ledger | `transfer.id` |
| `transfer.reversed` | Transfer reversed | Reverse ledger entry | `transfer.id` |
| `transfer.canceled` | Transfer canceled | Cancel ledger entry | `transfer.id` |

## Anti-Footgun Policy

**DO NOT** fulfill on both `checkout.session.completed` AND `payment_intent.succeeded`.

**Correct Pattern:**
1. Create order record on `checkout.session.completed`
2. Fulfill only on money-confirmed event (`payment_intent.succeeded` or `invoice.paid`)

## Event Flow Diagrams

### One-Time Payment Flow
```
Customer → Checkout → checkout.session.completed (create order)
                                    ↓
                    payment_intent.succeeded (fulfill order)
```

### Subscription Flow
```
Customer → Subscribe → customer.subscription.created (track)
                                    ↓
                    invoice.paid (grant access)
                                    ↓
                    customer.subscription.updated (update access)
```

