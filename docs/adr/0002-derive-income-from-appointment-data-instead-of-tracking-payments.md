---
status: accepted
---

# Derive income from appointment data instead of tracking payments

The business overview computes income from each appointment's frozen amounts, its status and its dates, and no payment is recorded anywhere. A deposit is assumed paid on the booking date and the balance on the appointment date. A Commission is paid out of the balance, so the deposit stays entirely with the owner. We chose this over payment tracking because the business does not want to record payments by hand and the rules are uniform enough to derive.

## Considered Options

- **Track real payments (paid flags or a payment ledger).** Rejected for now: it adds manual data entry the owner does not want.
- **Trigger the balance on the `completed` status.** Rejected for now: a shoot that has happened can still be in editing or review. Status will be set automatically from the data in a later feature, so the date is the source of truth.
- **Take the Commission from the whole price.** Rejected: the deposit is collected at booking, before any shoot, so the photographer is paid from the balance on the day.

## Consequences

- Income is an assumption, not a fact: a client who never paid the balance still counts once the appointment date passes.
- Reports are anchored on two dates: booking date for deposits and appointments made, appointment date for balances and Commission Payable. Both are read in the Paris time zone.
- A canceled appointment yields only its Retained Deposit, and a refunded one yields nothing.
- A Commission larger than the balance is reported as frozen and makes Owner Take negative on that appointment. A guard against it is a separate, later change.
- Introducing real payment tracking later means replacing the derivation, not extending it.
- The planned automatic status feature must stay consistent with the Balance Income date trigger.
