"""Tests for the typed blend range API (psd_tools.api.blend_range)."""

import numpy as np
import pytest

from ..utils import full_name


def test_blend_range_channel_from_raw() -> None:
    from psd_tools.api.blend_range import BlendRangeChannel

    raw = [
        (10 | (20 << 8), 30 | (40 << 8)),
        (50 | (60 << 8), 70 | (80 << 8)),
    ]
    channel = BlendRangeChannel.from_raw(raw)
    assert channel.this_layer_black == (10, 20)
    assert channel.this_layer_white == (30, 40)
    assert channel.underlying_black == (50, 60)
    assert channel.underlying_white == (70, 80)
    assert channel.to_raw() == raw


def test_blend_range_channel_default() -> None:
    from psd_tools.api.blend_range import BlendRangeChannel

    channel = BlendRangeChannel.default()
    assert channel.this_layer_black == (0, 255)
    assert channel.this_layer_white == (0, 255)
    assert channel.underlying_black == (0, 255)
    assert channel.underlying_white == (0, 255)
    assert channel.is_default
    assert not channel.this_layer_black_split
    assert not channel.this_layer_white_split
    assert not channel.underlying_black_split
    assert not channel.underlying_white_split
    assert isinstance(channel.describe(), str)
    assert channel.describe()


def test_blend_range_channel_mutable_and_split() -> None:
    from psd_tools.api.blend_range import BlendRangeChannel

    channel = BlendRangeChannel.default()
    channel.this_layer_black = (0, 128)
    assert channel.this_layer_black == (0, 128)
    assert not channel.is_default
    assert channel.this_layer_black_split
    assert not channel.underlying_black_split
    channel.this_layer_black = (0, 255)
    assert channel.is_default
    assert not channel.this_layer_black_split


def test_blend_range_channel_from_values() -> None:
    from psd_tools.api.blend_range import BlendRangeChannel

    channel = BlendRangeChannel.from_values()
    assert channel.is_default

    channel = BlendRangeChannel.from_values(
        this_layer_black=(0, 128), underlying_white=(10, 255)
    )
    assert channel.this_layer_black == (0, 128)
    assert channel.this_layer_white == (0, 255)
    assert channel.underlying_black == (0, 255)
    assert channel.underlying_white == (10, 255)
    assert not channel.is_default


def test_blend_ranges_container() -> None:
    from psd_tools.api.blend_range import BlendRangeChannel, BlendRanges

    composite = BlendRangeChannel.default()
    channels = [BlendRangeChannel.default() for _ in range(3)]
    ranges = BlendRanges(composite=composite, channels=channels)
    assert ranges.channel_count == 3
    assert len(ranges) == 3
    assert ranges[0] is channels[0]
    assert ranges[-1] is channels[2]
    assert list(ranges) == channels
    assert ranges.composite is composite
    assert ranges.is_default
    assert isinstance(ranges.describe(), str)
    assert ranges.describe()


def test_blend_ranges_from_raw() -> None:
    from psd_tools.api.blend_range import BlendRanges
    from psd_tools.psd.layer_and_mask import LayerBlendingRanges

    raw = LayerBlendingRanges(
        [(0, 255 << 8), (0, 65535)],
        [
            [(0, 65535), (0, 65535)],
            [(10, 20 << 8), (0, 65535)],
            [(0, 65535), (0, 65535)],
        ],
    )
    ranges = BlendRanges.from_raw(raw)
    assert ranges.composite.this_layer_black == (0, 255)
    assert ranges.composite.is_default is False
    assert ranges.channel_count == 3
    assert len(ranges) == 3
    assert ranges[0].is_default
    assert ranges[1].this_layer_black == (10, 20)
    assert ranges[-1].is_default
    assert not ranges.is_default


def test_blend_ranges_from_null() -> None:
    from psd_tools.api.blend_range import BlendRanges
    from psd_tools.psd.layer_and_mask import LayerBlendingRanges

    raw = LayerBlendingRanges(None, None)
    ranges = BlendRanges.from_raw(raw)
    assert ranges.channel_count == 0
    assert len(ranges) == 0
    assert list(ranges) == []
    assert ranges.composite.is_default


def test_blend_ranges_from_channels_and_apply_to_raw() -> None:
    from psd_tools.api.blend_range import BlendRangeChannel, BlendRanges
    from psd_tools.psd.layer_and_mask import LayerBlendingRanges

    composite = BlendRangeChannel.from_values(this_layer_black=(0, 128))
    channel = BlendRangeChannel.from_values(underlying_white=(10, 255))
    ranges = BlendRanges.from_channels(composite, [channel])
    assert ranges.composite.this_layer_black == (0, 128)
    assert ranges[0].underlying_white == (10, 255)

    raw = LayerBlendingRanges()
    ranges.apply_to_raw(raw)
    assert raw.composite_ranges == [(0, 128 << 8), (0, 65535)]
    assert raw.channel_ranges == [[(0, 65535), (10 | (255 << 8))]]


def test_blend_ranges_is_default() -> None:
    from psd_tools.api.blend_range import BlendRangeChannel, BlendRanges

    ranges = BlendRanges.from_channels(
        BlendRangeChannel.default(), [BlendRangeChannel.default()]
    )
    assert ranges.is_default

    ranges = BlendRanges.from_channels(
        BlendRangeChannel.default(),
        [BlendRangeChannel.from_values(this_layer_white=(0, 128))],
    )
    assert not ranges.is_default

    ranges = BlendRanges.from_channels(
        BlendRangeChannel.from_values(underlying_black=(0, 128)),
        [BlendRangeChannel.default()],
    )
    assert not ranges.is_default


def test_blend_ranges_compute_visibility() -> None:
    from psd_tools.api.blend_range import BlendRangeChannel, BlendRanges

    source = np.full((2, 3, 3), 0.5, dtype=np.float32)
    backdrop = np.full((2, 3, 3), 0.5, dtype=np.float32)

    ranges = BlendRanges.from_channels(BlendRangeChannel.default(), [])
    weight = ranges.compute_visibility(source, backdrop)
    assert weight.shape == (2, 3, 1)
    assert np.all(weight >= 0.0)
    assert np.all(weight <= 1.0)
    assert np.allclose(weight, 1.0)

    # "This Layer" black slider at (0, 255): weight = luminosity / 255.
    ranges = BlendRanges.from_channels(
        BlendRangeChannel.from_values(this_layer_black=(0, 255)), []
    )
    weight = ranges.compute_visibility(source, backdrop)
    assert weight.shape == (2, 3, 1)
    assert np.allclose(weight, 0.5, atol=1e-3)

    # "Underlying Layer" black slider at (0, 255): uses backdrop values.
    ranges = BlendRanges.from_channels(
        BlendRangeChannel.from_values(underlying_black=(0, 255)), []
    )
    weight = ranges.compute_visibility(source, backdrop)
    assert np.allclose(weight, 0.5, atol=1e-3)


def test_blend_ranges_to_pil_mask() -> None:
    from psd_tools.api.blend_range import BlendRangeChannel, BlendRanges

    source = np.full((2, 3, 3), 0.5, dtype=np.float32)
    backdrop = np.full((2, 3, 3), 0.5, dtype=np.float32)

    ranges = BlendRanges.from_channels(
        BlendRangeChannel.from_values(this_layer_black=(0, 255)), []
    )
    mask = ranges.to_pil_mask(source, backdrop)
    assert mask.mode == "L"
    assert mask.size == (3, 2)
    assert 120 <= mask.getpixel((0, 0)) <= 135

    ranges = BlendRanges.from_channels(BlendRangeChannel.default(), [])
    mask = ranges.to_pil_mask(source, backdrop)
    assert mask.mode == "L"
    assert mask.getpixel((0, 0)) == 255


def test_layer_blend_ranges_default() -> None:
    from psd_tools.api.psd_image import PSDImage

    psd = PSDImage.open(full_name("layers/pixel-layer.psd"))
    layer = psd[0]
    ranges = layer.blend_ranges
    assert ranges.is_default
    assert ranges.channel_count == 4
    assert len(ranges) == 4
    assert ranges.composite.is_default


def test_layer_blend_ranges_setter_persists(tmp_path) -> None:
    from psd_tools.api.blend_range import BlendRangeChannel, BlendRanges
    from psd_tools.api.psd_image import PSDImage

    psd = PSDImage.open(full_name("layers/pixel-layer.psd"))
    layer = psd[0]

    composite = BlendRangeChannel.from_values(this_layer_black=(0, 128))
    ranges = BlendRanges.from_channels(
        composite, [BlendRangeChannel.default() for _ in range(4)]
    )
    layer.blend_ranges = ranges

    # The change is reflected in the underlying record.
    assert layer._record.blending_ranges.composite_ranges == [
        (0, 128 << 8),
        (0, 65535),
    ]
    assert layer.blend_ranges.composite.this_layer_black == (0, 128)
    assert not layer.blend_ranges.is_default

    # The change persists through save.
    output_path = str(tmp_path / "out.psd")
    psd.save(output_path)
    reloaded = PSDImage.open(output_path)
    assert reloaded[0].blend_ranges.composite.this_layer_black == (0, 128)
    assert reloaded[0].blend_ranges.channel_count == 4
    assert not reloaded[0].blend_ranges.is_default
