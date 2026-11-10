"""Tests for Garage, derived from SPEC.md."""

import pytest
from datetime import datetime, timedelta

from garage import Garage

T0 = datetime(2026, 3, 2, 9, 0, 0)


# ---------------------------------------------------------------- construction

def test_capacity_zero_rejected():
    with pytest.raises(ValueError):
        Garage(0)


def test_negative_capacity_rejected():
    with pytest.raises(ValueError):
        Garage(-3)


def test_capacity_one_ok():
    assert Garage(1).capacity == 1


# ---------------------------------------------------------------- plate rules

def test_plate_normalization_equivalence():
    g = Garage(3)
    assert g.enter("ab 123", T0)
    assert g.occupancy() == 1
    with pytest.raises(ValueError):
        g.enter("AB-123", T0)  # same car, already inside
    assert g.exit("ab123", T0 + timedelta(hours=1)) == 2.0


@pytest.mark.parametrize("plate", ["", "   ", "-", "--", " - "])
def test_empty_plate_rejected(plate):
    g = Garage(2)
    with pytest.raises(ValueError):
        g.enter(plate, T0)
    with pytest.raises(ValueError):
        g.exit(plate, T0)
    with pytest.raises(ValueError):
        g.lost_ticket(plate, T0)
    with pytest.raises(ValueError):
        g.add_pass(plate, 2026, 3)
    assert g.occupancy() == 0


# ---------------------------------------------------------------- basic billing

def test_two_hour_visit():
    g = Garage(capacity=2)
    assert g.enter("AB-123", T0)
    assert g.exit("AB-123", T0 + timedelta(hours=2)) == 4.0


def test_grace_period_free():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(minutes=15)) == 0.0


def test_just_over_grace_costs_one_hour():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(minutes=16)) == 2.0


def test_fractional_minutes_round_up():
    g = Garage(2)
    g.enter("A1", T0)
    # 15 min 1 s -> 16 minutes -> 1 started hour
    assert g.exit("A1", T0 + timedelta(minutes=15, seconds=1)) == 2.0


def test_started_hour_billing():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(hours=1, minutes=1)) == 4.0


def test_daily_cap_15():
    g = Garage(2)
    g.enter("A1", T0)
    # 23 hours -> 23 started hours * $2 = $46, capped at $15
    assert g.exit("A1", T0 + timedelta(hours=23)) == 15.0


def test_two_day_cap():
    g = Garage(2)
    g.enter("A1", T0)
    # 48 hours -> 2 periods * $15
    assert g.exit("A1", T0 + timedelta(hours=48)) == 30.0


def test_periods_start_at_first_admission():
    g = Garage(2)
    g.enter("A1", T0)
    # 24h + 1h -> 25 started hours: first 24 capped at $15, +1h = $2
    assert g.exit("A1", T0 + timedelta(hours=25)) == 17.0


def test_exact_24h_is_one_period():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(hours=24)) == 15.0


def test_zero_duration_exit():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.exit("A1", T0) == 0.0


# ---------------------------------------------------------------- capacity

def test_full_garage_rejects_without_changes():
    g = Garage(1)
    assert g.enter("A1", T0)
    assert g.enter("B2", T0) is False
    assert g.occupancy() == 1
    # rejected car has no session: it can enter later and is billed from then
    assert g.exit("A1", T0 + timedelta(hours=1)) == 2.0
    assert g.enter("B2", T0 + timedelta(hours=2))
    assert g.exit("B2", T0 + timedelta(hours=3)) == 2.0


def test_enter_already_inside_raises():
    g = Garage(2)
    g.enter("A1", T0)
    with pytest.raises(ValueError):
        g.enter("A1", T0 + timedelta(minutes=5))
    assert g.occupancy() == 1


# ---------------------------------------------------------------- exit checks

def test_exit_not_inside_raises():
    g = Garage(2)
    with pytest.raises(ValueError):
        g.exit("A1", T0)


def test_exit_before_latest_admission_raises():
    g = Garage(2)
    g.enter("A1", T0)
    with pytest.raises(ValueError):
        g.exit("A1", T0 - timedelta(minutes=1))
    # still inside, can leave normally
    assert g.exit("A1", T0 + timedelta(hours=1)) == 2.0


def test_lost_ticket_not_inside_raises():
    g = Garage(2)
    with pytest.raises(ValueError):
        g.lost_ticket("A1", T0)


def test_lost_ticket_before_admission_raises():
    g = Garage(2)
    g.enter("A1", T0)
    with pytest.raises(ValueError):
        g.lost_ticket("A1", T0 - timedelta(seconds=1))


# ---------------------------------------------------------------- re-entry

def test_reentry_within_10_minutes_resumes_session():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(minutes=30)) == 2.0
    g.enter("A1", T0 + timedelta(minutes=40))  # 10 min after exit
    # session spans 90 minutes from first admission -> 2 started hours = $4,
    # minus $2 already paid
    assert g.exit("A1", T0 + timedelta(minutes=90)) == 2.0


def test_reentry_outside_window_starts_new_session():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(minutes=30)) == 2.0
    g.enter("A1", T0 + timedelta(minutes=41))  # 11 min after exit
    # new session: 30 minutes -> 1 started hour
    assert g.exit("A1", T0 + timedelta(minutes=71)) == 2.0


def test_reentry_after_lost_ticket_starts_new_session():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.lost_ticket("A1", T0 + timedelta(minutes=30)) == 15.0
    g.enter("A1", T0 + timedelta(minutes=35))
    assert g.exit("A1", T0 + timedelta(minutes=45)) == 0.0  # 10 min, grace


def test_reentry_after_grace_exit_still_resumes():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(minutes=5)) == 0.0
    g.enter("A1", T0 + timedelta(minutes=10))
    # resumed: 20 minutes total -> 1 started hour
    assert g.exit("A1", T0 + timedelta(minutes=20)) == 2.0


def test_reentry_span_includes_time_outside():
    g = Garage(2)
    g.enter("A1", T0)
    g.exit("A1", T0 + timedelta(minutes=10))  # free
    g.enter("A1", T0 + timedelta(minutes=20))
    # 40 minutes total span -> 1 started hour
    assert g.exit("A1", T0 + timedelta(minutes=40)) == 2.0


def test_reentry_after_lost_then_exit_resumes():
    g = Garage(2)
    g.enter("A1", T0)
    g.lost_ticket("A1", T0 + timedelta(minutes=10))
    g.enter("A1", T0 + timedelta(minutes=20))  # new session
    assert g.exit("A1", T0 + timedelta(minutes=30)) == 0.0
    g.enter("A1", T0 + timedelta(minutes=35))  # resumes the new session
    assert g.exit("A1", T0 + timedelta(minutes=40)) == 2.0  # 20 min total


# ---------------------------------------------------------------- lost ticket

def test_lost_ticket_minimum_15():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.lost_ticket("A1", T0 + timedelta(minutes=30)) == 15.0


def test_lost_ticket_grace_still_15():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.lost_ticket("A1", T0 + timedelta(minutes=5)) == 15.0


def test_lost_ticket_larger_charge_kept():
    g = Garage(2)
    g.enter("A1", T0)
    assert g.lost_ticket("A1", T0 + timedelta(hours=2)) == 15.0  # max(4, 15)
    g.enter("A1", T0 + timedelta(hours=3))
    assert g.lost_ticket("A1", T0 + timedelta(hours=10)) == 15.0  # max(20, 15)


def test_lost_ticket_frees_space():
    g = Garage(1)
    g.enter("A1", T0)
    g.lost_ticket("A1", T0 + timedelta(minutes=1))
    assert g.occupancy() == 0
    assert g.enter("B2", T0 + timedelta(minutes=2))


# ---------------------------------------------------------------- passes

def test_pass_makes_session_free():
    g = Garage(2)
    g.add_pass("A1", 2026, 3)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(hours=3)) == 0.0


def test_pass_applies_to_lost_ticket():
    g = Garage(2)
    g.add_pass("A1", 2026, 3)
    g.enter("A1", T0)
    assert g.lost_ticket("A1", T0 + timedelta(minutes=5)) == 0.0


def test_pass_plate_normalized():
    g = Garage(2)
    g.add_pass("a-1", 2026, 3)
    g.enter("A 1", T0)
    assert g.exit("A1", T0 + timedelta(hours=2)) == 0.0


def test_pass_wrong_month_not_free():
    g = Garage(2)
    g.add_pass("A1", 2026, 4)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(hours=2)) == 4.0


def test_pass_wrong_year_not_free():
    g = Garage(2)
    g.add_pass("A1", 2027, 3)
    g.enter("A1", T0)
    assert g.exit("A1", T0 + timedelta(hours=2)) == 4.0


def test_pass_keyed_on_first_admission_month():
    g = Garage(2)
    g.add_pass("A1", 2026, 3)
    g.enter("A1", T0)
    g.exit("A1", T0 + timedelta(minutes=30))
    g.enter("A1", T0 + timedelta(minutes=40))  # resumes March session
    # session's first admission is in March -> free
    assert g.exit("A1", T0 + timedelta(hours=2)) == 0.0


def test_pass_does_not_cover_new_session_next_month():
    g = Garage(2)
    g.add_pass("A1", 2026, 3)
    g.enter("A1", T0)
    g.exit("A1", T0 + timedelta(minutes=30))
    g.enter("A1", T0 + timedelta(days=30))  # April, new session
    assert g.exit("A1", T0 + timedelta(days=30, hours=2)) == 4.0


def test_pass_added_after_session_start_still_covers_it():
    g = Garage(2)
    g.enter("A1", T0)
    g.add_pass("A1", 2026, 3)
    assert g.exit("A1", T0 + timedelta(hours=2)) == 0.0


# ---------------------------------------------------------------- occupancy

def test_occupancy_tracks_cars():
    g = Garage(3)
    assert g.occupancy() == 0
    g.enter("A1", T0)
    g.enter("B2", T0)
    assert g.occupancy() == 2
    g.exit("A1", T0 + timedelta(minutes=1))
    assert g.occupancy() == 1
    g.lost_ticket("B2", T0 + timedelta(minutes=2))
    assert g.occupancy() == 0


# ---------------------------------------------------------------- multiple cars

def test_independent_sessions_per_car():
    g = Garage(2)
    g.enter("A1", T0)
    g.enter("B2", T0 + timedelta(minutes=30))
    assert g.exit("A1", T0 + timedelta(hours=1)) == 2.0
    assert g.exit("B2", T0 + timedelta(hours=1, minutes=30)) == 2.0
    assert g.occupancy() == 0


def test_reentry_of_one_car_does_not_affect_other():
    g = Garage(2)
    g.enter("A1", T0)
    g.enter("B2", T0)
    g.exit("A1", T0 + timedelta(minutes=30))
    g.enter("A1", T0 + timedelta(minutes=40))
    assert g.exit("B2", T0 + timedelta(hours=1)) == 2.0
    assert g.exit("A1", T0 + timedelta(minutes=90)) == 2.0
