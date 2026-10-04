---
status: accepted
---

# Snapshot price per Appointment Add-on and fold totals into the appointment

Each Appointment Add-on freezes its unit price and unit commission when it is booked, and the add-on totals are folded into the appointment's `price_at_booking`, `remaining_amount` and `commission_amount_at_booking`. We chose this over keeping those fields package-only because anything reading the appointment (frontend, refunds, payouts) then sees the full amount owed without summing, and a catalogue price change never alters what a client already accepted.

## Considered Options

- **Package-only appointment totals, add-on totals computed from the rows.** Rejected: every reader must remember to add the two, and the refund and cancellation flow would silently ignore add-ons.
- **Re-read the catalogue price on quantity change.** Rejected: changing a quantity would re-price a line the client already agreed to.

## Consequences

- Appointment totals must be recomputed on every add, remove, quantity change and resolution of an Unresolved Add-on.
- The appointment totals are no longer the package price alone, so code that assumes `price_at_booking` equals the package price must be revisited.
