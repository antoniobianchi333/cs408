"""Parking garage with sessions, re-entry, lost tickets and monthly passes. See SPEC.md."""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

GRACE = timedelta(minutes=15)
REENTRY_WINDOW = timedelta(minutes=10)
HOURLY = Decimal("2.00")
PERIOD_CAP = Decimal("15.00")
LOST_MINIMUM = Decimal("15.00")
HOURS_PER_PERIOD = 24


@dataclass
class _Session:
    start: datetime
    paid: Decimal = Decimal("0")
    closed_at: datetime | None = None
    resumable: bool = False


def _normalize(plate: str) -> str:
    norm = plate.replace(" ", "").replace("-", "").upper()
    if not norm:
        raise ValueError("empty plate")
    return norm


def _charge(start: datetime, t: datetime) -> Decimal:
    minutes = math.ceil((t - start).total_seconds() / 60)
    if minutes <= GRACE.total_seconds() / 60:
        return Decimal("0")
    hours = math.ceil(minutes / 60)
    full_periods, rest = divmod(hours, HOURS_PER_PERIOD)
    return full_periods * PERIOD_CAP + min(rest * HOURLY, PERIOD_CAP)


def _money(x: Decimal) -> float:
    return float(x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class Garage:
    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._inside: dict[str, datetime] = {}
        self._sessions: dict[str, _Session] = {}
        self._passes: set[tuple[str, int, int]] = set()

    def occupancy(self) -> int:
        return len(self._inside)

    def add_pass(self, plate: str, year: int, month: int) -> None:
        self._passes.add((_normalize(plate), year, month))

    def enter(self, plate: str, t: datetime) -> bool:
        car = _normalize(plate)
        if car in self._inside:
            raise ValueError("car is already inside")
        if len(self._inside) >= self.capacity:
            return False
        previous = self._sessions.get(car)
        resumes = previous is not None and previous.resumable and t - previous.closed_at <= REENTRY_WINDOW
        if not resumes:
            self._sessions[car] = _Session(start=t)
        self._inside[car] = t
        return True

    def exit(self, plate: str, t: datetime) -> float:
        return self._leave(plate, t, lost=False)

    def lost_ticket(self, plate: str, t: datetime) -> float:
        return self._leave(plate, t, lost=True)

    def _leave(self, plate: str, t: datetime, lost: bool) -> float:
        car = _normalize(plate)
        if car not in self._inside:
            raise ValueError("car is not inside")
        if t < self._inside[car]:
            raise ValueError("leaving before latest admission")
        session = self._sessions[car]
        charge = _charge(session.start, t)
        if lost:
            charge = max(charge, LOST_MINIMUM)
        if (car, session.start.year, session.start.month) in self._passes:
            charge = Decimal("0")
        due = max(charge - session.paid, Decimal("0"))
        session.paid += due
        session.closed_at = t
        session.resumable = not lost
        del self._inside[car]
        return _money(due)
