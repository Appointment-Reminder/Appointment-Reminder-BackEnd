# Photo Reminder

Appointment booking for photography businesses: clients book a Package (plus optional Add-ons) through a Jotform or the frontend, and business members earn commission on what they perform.

## Language

**Package**:
The main service a client books, with a category, a duration, and a versioned price that includes a deposit.
_Avoid_: Product, offer

**Package Category**:
A business-defined grouping of Packages, used to assign members to bookings.
_Avoid_: Type, group

**Alias**:
The label a Jotform answer uses to refer to a Package or Add-on, matched against the submission to identify it.
_Avoid_: Slug, code

**Add-on**:
An optional extra service booked alongside a Package. It is owned by a business, may be restricted to one Package Category, has an Alias and a price, and may or may not carry a duration and a quantity (see Add-on Type).
_Avoid_: Extra, adds_ons, upgrade

**Add-on Type**:
Whether an Add-on carries a duration and whether it can be booked in a quantity above 1. An Add-on without a quantity is always booked once, and one without a duration adds no time. It cannot change once the Add-on has been booked.
_Avoid_: Kind, category (a Package Category is something else)

**Add-on Price**:
The single amount charged for an Add-on from an effective date onward. It has no deposit; it is added to the appointment's remaining balance.
_Avoid_: Add-on fee

**Appointment Add-on**:
An Add-on booked on one appointment, with a quantity (at least 1, always 1 if the Add-on has no quantity) and the price and commission frozen at the time it was booked. An appointment holds at most one per Add-on.
_Avoid_: Booked extra

**Commission**:
The share of a Package's or Add-on's price earned by a business member, either a percentage or a flat amount, defined per member and per Package or Add-on. A missing commission means 0.
_Avoid_: Cut, fee

**Commission Correction**:
Fixing a mistake in an existing Commission version in place, instead of adding a new dated version. It only affects bookings made afterwards: Appointment Add-ons keep the commission frozen when they were booked.
_Avoid_: Commission update (ambiguous with adding a new version)

**Unresolved Add-on**:
An Add-on label from a Jotform submission that matched no Add-on Alias. It is kept on the appointment and flagged for manual resolution without blocking the Package booking.
