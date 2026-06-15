# Project Facts

Stable facts about the system under test. Multiple skills reference this so the
"what exists" knowledge has one home.

> This is a fictional sample app used only to make the demo concrete. All names,
> modules, and accounts below are invented.

## Product

**ShopKit** — a fictional demo e-commerce app (browse, cart, checkout).

## Modules

- **Auth** — sign up, log in, session, password reset.
- **Catalog** — product listing, search, filters.
- **Cart** — add/remove items, quantities, promo codes.
- **Checkout** — address, shipping options, order placement.
- **Payments** — card and wallet, refunds.
- **Orders** — order history, tracking, returns.
- **Account** — profile, saved addresses, preferences.

## Environments

- **staging** — safe for destructive tests; data reset nightly.
- **prod** — read-only for QA; never seed or delete data here.

## Test accounts (illustrative)

- `admin@example.test` — full-permission admin account.
- `customer@example.test` — standard shopper account.
- Accounts live in the secret store; never hardcode passwords in tests or reports.

## Build variants

- `debug` — verbose logging, dev menu enabled.
- `release` — production parity; used for sign-off.

## Known constraints

- Time-sensitive features (promo expiry, "new arrivals") need seeded data with
  correct timestamps — live data is unreliable for asserting them.
- Analytics tiles can have ingestion lag; assert against the source of truth, not
  the dashboard number.
