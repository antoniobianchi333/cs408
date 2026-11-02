"""Tests for LayerBlendingRanges write validation."""

import io

import pytest

from psd_tools.psd.layer_and_mask import LayerBlendingRanges


def test_write_valid_ranges() -> None:
    element = LayerBlendingRanges(
        [(0, 1), (0, 1)],
        [
            [(0, 1), (0, 1)],
            [(0, 1), (0, 1)],
        ],
    )
    fp = io.BytesIO()
    element.write(fp)
    fp.seek(0)
    new_element = LayerBlendingRanges.read(fp)
    assert element == new_element


def test_write_invalid_composite_ranges() -> None:
    with pytest.raises(ValueError):
        element = LayerBlendingRanges(
            [(0, 1)],
            [
                [(0, 1), (0, 1)],
                [(0, 1), (0, 1)],
            ],
        )
        element.write(io.BytesIO())


def test_write_invalid_channel_ranges() -> None:
    with pytest.raises(ValueError):
        element = LayerBlendingRanges(
            [(0, 1), (0, 1)],
            [
                [(0, 1)],
                [(0, 1), (0, 1)],
            ],
        )
        element.write(io.BytesIO())
