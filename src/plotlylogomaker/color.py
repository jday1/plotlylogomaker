# Whether to color by chemical properties or as in DMS-Tools: https://jbloomlab.github.io/dms_tools2/prefs.html

import re

from pydantic import BaseModel, field_validator


class Color(BaseModel):
    hex: str
    name: str

    @field_validator("hex")
    def validate_hex(cls, hex: str) -> str:
        if not bool(re.fullmatch(r"#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})", hex)):
            raise ValueError(f"Invalid hex color code: '{hex}'. Must be in the format '#RRGGBB' or '#RGB'.")
        return hex


class ColorScheme(BaseModel):
    colors: dict[str, Color]
    title: str

    @field_validator("colors")
    def validate_residues(cls, colors: dict[str, Color]) -> dict[str, Color]:
        present = set()
        for group in colors.keys():
            for residue in group:
                if residue in present:
                    raise ValueError(f"Value '{residue}' appears more than once.")
                present.add(residue)
        return colors

    @property
    def valid_residues(self) -> set[str]:
        """
        Returns the valid residues for the color schema.
        """
        return {residue for residues in self.colors.keys() for residue in residues}

    @property
    def hex_lookup(self) -> dict[str, str]:
        """
        Returns a dictionary with the hex values of the colors.
        """
        return {aa: color.hex for group, color in self.colors.items() for aa in group}

    @property
    def name_lookup(self) -> dict[str, str]:
        """
        Returns a dictionary with the names of the colors.
        """
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
