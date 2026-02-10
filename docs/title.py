# %%
import string
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative

from plotlylogomaker.color import Color, ColorScheme
from plotlylogomaker.logo import Logo, add_logo

PLOTLYLOGOMAKER_PATH = Path("docs")

np.random.seed(100)

frequencies = pd.DataFrame(
    [
        [
            np.random.uniform(0.5, 0.8) * (1 if aa == upper_char else -1 if aa == lower_char else 0)
            for aa in string.ascii_uppercase
        ]
        for upper_char, lower_char in zip("PLOTLY   ", "LOGOMAKER")
    ],
    columns=tuple(string.ascii_uppercase),
)

PLOTLY_COLOR_SCHEME = ColorScheme(
    colors={
        letter: Color(
            hex=qualitative.Alphabet[i % len(qualitative.Alphabet)],
            name=f"Plotly {i}",
        )
        for i, letter in enumerate(string.ascii_uppercase)
    },
    title="Plotly Qualitative",
)

title_logo = Logo(
    df=frequencies,
    legend=False,
    color_scheme=PLOTLY_COLOR_SCHEME,
    hover=True,
    reflect_negative_symbols=False,
)

# single plot figure
fig: go.Figure = go.Figure()
add_logo(title_logo, fig)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    height=400,
    width=800,
)
fig.write_image(PLOTLYLOGOMAKER_PATH / "title_logo.svg")
# %%
