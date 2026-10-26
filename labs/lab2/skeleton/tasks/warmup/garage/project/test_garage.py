from datetime import datetime, timedelta

from garage import Garage

T0 = datetime(2026, 3, 2, 9, 0, 0)


def test_two_hour_visit():
    g = Garage(capacity=2)
    assert g.enter("AB-123", T0)
    assert g.exit("AB-123", T0 + timedelta(hours=2)) == 4.0
