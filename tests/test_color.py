import pytest
from pydantic import ValidationError

from plotlylogomaker.color import Color, ColorScheme  # replace with your actual module


def valid_colors():
    """Return a valid color mapping covering all 20 amino acids exactly once."""
    groups = ["AG", "CST", "DE", "FWY", "HKR", "ILMPV", "NQ"]
    colors = {g: Color(hex="#123abc", name="Group") for g in groups}
    return colors


def test_duplicate_amino_acid():
    colors = valid_colors()
    # Introduce a duplication: 'A' appears in both 'AG' and 'A'
    colors["A"] = Color(hex="#abcdef", name="Extra A")
    with pytest.raises(ValidationError, match="appears more than once"):
        ColorScheme(colors=colors, title="Test")


def test_invalid_hex_code():
    # Introduce invalid hex code
    with pytest.raises(ValidationError, match="Invalid hex color code"):
        Color(hex="123456", name="No hash")  # missing `#`

    with pytest.raises(ValidationError, match="Invalid hex color code"):
        Color(hex="#12345G", name="Bad hex char")  # 'G' is invalid

    with pytest.raises(ValidationError, match="Invalid hex color code"):
        Color(hex="#1234", name="Too short")  # not 3 or 6 digits
