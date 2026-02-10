"""Defines the Color and ColorScheme classes for managing color schemes in the logo generation process."""

import re

from pydantic import BaseModel, field_validator


class Color(BaseModel):
    """Defines a color with a hex code and a name."""

    hex: str
    name: str

    @field_validator("hex")
    def validate_hex(cls, hex: str) -> str:
        """Validate that the hex color code is in the correct format."""
        if not bool(re.fullmatch(r"#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})", hex)):
            raise ValueError(
                f"Invalid hex color code: '{hex}'. Must be in the format '#RRGGBB' or '#RGB'."
            )
        return hex


class ColorScheme(BaseModel):
    """Defines a color scheme for the logo, mapping groups of keys to specific colors."""

    colors: dict[str, Color]
    title: str

    @field_validator("colors")
    def validate_keys(cls, colors: dict[str, Color]) -> dict[str, Color]:
        """Validate that keys are not duplicated between groups."""
        present = set()
        for group in colors.keys():
            for key in group:
                if key in present:
                    raise ValueError(f"Value '{key}' appears more than once.")
                present.add(key)
        return colors

    @property
    def valid_keys(self) -> set[str]:
        """Returns the valid keys for the color schema."""
        return {key for keys in self.colors.keys() for key in keys}

    @property
    def hex_lookup(self) -> dict[str, str]:
        """Returns a dictionary with the hex values of the colors."""
        return {aa: color.hex for group, color in self.colors.items() for aa in group}

    @property
    def name_lookup(self) -> dict[str, str]:
        """Returns a dictionary with the names of the colors."""
        return {aa: color.name for group, color in self.colors.items() for aa in group}


DMS_COLOR_SCHEME = ColorScheme(
    colors={
        "AG": Color(hex="#f76ab4", name="Small"),
        "CST": Color(hex="#ff7f00", name="Polar"),
        "DE": Color(hex="#e41a1c", name="Acidic"),
        "FWY": Color(hex="#84380b", name="Aromatic"),
        "HKR": Color(hex="#3c58e5", name="Basic"),
        "ILMPV": Color(hex="#12ab0d", name="Hydrophobic"),
        "NQ": Color(hex="#972aa8", name="Amide"),
    },
    title="DMS",
)

CHEMICAL_COLOR_SCHEME = ColorScheme(
    colors={
        "GSTYC": Color(hex="#21d426", name="Polar"),
        "QN": Color(hex="#d41cbf", name="Amide"),
        "KRH": Color(hex="#0517bd", name="Basic"),
        "DE": Color(hex="#d40a14", name="Acidic"),
        "AVLIPWFM": Color(hex="#000000", name="Hydrophobic"),
    },
    title="Chemical",
)

NUCLEOTIDE_COLOR_SCHEME = ColorScheme(
    colors={
        "A": Color(hex="#1f77b4", name="Adenine"),
        "C": Color(hex="#ff7f0e", name="Cytosine"),
        "G": Color(hex="#2ca02c", name="Guanine"),
        "T": Color(hex="#d62728", name="Thymine"),
    },
    title="Nucleotide",
)
