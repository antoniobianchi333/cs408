# Garage specification

`Garage(capacity)` models a parking garage. All times are naive `datetime` objects. Money amounts are
returned as `float` values rounded to cents (ties rounded up).

## Construction

- `capacity` is the number of spaces. It must be at least 1, otherwise `ValueError`.

## Plates

- A plate is normalized by removing spaces and hyphens and converting to upper case. Two plates denote the
  same car exactly when their normalized forms are equal.
- A plate that is empty after normalization raises `ValueError` in every method that takes a plate.

## Sessions

A **session** is one continuous paid use of the garage by one car. A session starts when a car is
admitted without resuming an earlier session. A session can span several visits: see *Re-entry*.

The **session charge** at time `t` is computed over the span from the session's first admission to `t`,
including any time the car spent outside the garage between visits:

1. The span is rounded up to whole minutes. A span of at most 15 minutes costs `0.00`.
2. Otherwise the span is billed at $2.00 per started hour.
3. The span is divided into consecutive 24-hour periods starting at the session's first admission. Each
   period (with the started hours that begin in it) costs at most $15.00.

## Methods

### `enter(plate, t) -> bool`

- If the car is already inside: `ValueError`.
- If no space is free: return `False`. Nothing changes.
- Otherwise the car is admitted and `True` is returned. The car **resumes** its previous session (instead
  of starting a new one) if and only if that session ended with `exit` (not `lost_ticket`) at most
  10 minutes before `t`.

### `exit(plate, t) -> float`

- If the car is not inside: `ValueError`. If `t` is earlier than the car's latest admission: `ValueError`.
- The car leaves and frees its space. The method returns the **amount due**: the session charge at `t`
  minus everything already paid in this session, but never less than `0.00`.

### `lost_ticket(plate, t) -> float`

- Same checks and effects as `exit`, except that the session charge used for the amount due is at least
  $15.00. A session that ended with `lost_ticket` can never be resumed.

### `add_pass(plate, year, month)`

- Registers a monthly pass. Every session whose **first admission** falls in that calendar month is free:
  all its `exit` and `lost_ticket` calls return `0.00`.

### `occupancy() -> int`

- The number of cars currently inside.
