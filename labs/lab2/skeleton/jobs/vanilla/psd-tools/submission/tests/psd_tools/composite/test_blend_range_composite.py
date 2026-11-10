"""Tests that the compositing engine applies blend-if (blend ranges)."""

import numpy as np
import pytest
from PIL import Image

from psd_tools import PSDImage
from psd_tools.composite import composite
from psd_tools.psd.layer_and_mask import LayerBlendingRanges

FULL = (0, 65535)


def _make_psd(values: np.ndarray) -> PSDImage:
    """Create a new RGB PSD with a single opaque pixel layer."""
    height, width = values.shape[:2]
    psd = PSDImage.new("RGB", (width, height))
    image = Image.fromarray(values.astype(np.uint8), "RGB")
    psd.create_pixel_layer(image, name="L")
    return psd


def _gradient_layer() -> np.ndarray:
    """4x4 layer with per-column luminosity 0, 64, 191, 255."""
    columns = np.array([0, 64, 191, 255], dtype=np.uint8)
    return np.stack([np.tile(columns, (4, 1))] * 3, axis=2)


def _set_ranges(layer, composite_ranges, channel_ranges=None) -> None:
    if channel_ranges is None:
        channel_ranges = [[FULL, FULL]] * 4
    layer._record.blending_ranges = LayerBlendingRanges(
        composite_ranges, channel_ranges
    )


def test_composite_ignores_default_ranges() -> None:
    psd = _make_psd(_gradient_layer())
    layer = psd[0]
    _set_ranges(layer, [FULL, FULL])
    color, shape, alpha = composite(layer)
    assert np.allclose(alpha, 1.0)


def test_composite_this_layer_black() -> None:
    # this_layer_black = (0, 255): weight = luminosity / 255.
    psd = _make_psd(_gradient_layer())
    layer = psd[0]
    _set_ranges(layer, [(0, 255 << 8), FULL])
    color, shape, alpha = composite(layer)
    expected = np.array([0.0, 64 / 255, 191 / 255, 1.0])
    assert np.allclose(alpha[0], expected, atol=1e-3)


def test_composite_this_layer_white() -> None:
    # this_layer_white = (0, 255): weight = 1 - luminosity / 255.
    psd = _make_psd(_gradient_layer())
    layer = psd[0]
    _set_ranges(layer, [FULL, (0, 255 << 8)])
    color, shape, alpha = composite(layer)
    expected = np.array([1.0, 1 - 64 / 255, 1 - 191 / 255, 0.0])
    assert np.allclose(alpha[0], expected, atol=1e-3)


def test_composite_split_slider_fades() -> None:
    # this_layer_black = (0, 128): weight = luminosity / 128, clamped at 1.
    psd = _make_psd(_gradient_layer())
    layer = psd[0]
    _set_ranges(layer, [(0, 128 << 8), FULL])
    color, shape, alpha = composite(layer)
    expected = np.array([0.0, 64 / 128, 1.0, 1.0])
    assert np.allclose(alpha[0], expected, atol=1e-3)


def test_composite_underlying_layer_black() -> None:
    # underlying_black = (0, 255): weight = backdrop luminosity / 255.
    psd = _make_psd(_gradient_layer())
    layer = psd[0]
    _set_ranges(layer, [FULL, (0, 255 << 8)])
    color, shape, alpha = composite(layer, color=0.5, alpha=1.0)
    assert np.allclose(alpha, 0.5, atol=1e-3)


def test_composite_per_channel_range() -> None:
    # Red channel this_layer_black = (0, 255): weight = R / 255.
    values = np.zeros((4, 4, 3), dtype=np.uint8)
    values[:, :, 0] = np.tile(np.array([0, 64, 191, 255], dtype=np.uint8), (4, 1))
    values[:, :, 1] = 255
    values[:, :, 2] = 255
    psd = _make_psd(values)
    layer = psd[0]
    _set_ranges(
        layer,
        [FULL, FULL],
        [
            [(0, 255 << 8), FULL],
            [FULL, FULL],
            [FULL, FULL],
            [FULL, FULL],
        ],
    )
    color, shape, alpha = composite(layer)
    expected = np.array([0.0, 64 / 255, 191 / 255, 1.0])
    assert np.allclose(alpha[0], expected, atol=1e-3)
