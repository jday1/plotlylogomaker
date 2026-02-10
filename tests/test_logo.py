from unittest.mock import patch

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest
from plotly.subplots import make_subplots

from plotlylogomaker.color import CHEMICAL_COLOR_SCHEME, DMS_COLOR_SCHEME, NUCLEOTIDE_COLOR_SCHEME
from plotlylogomaker.logo import Logo, add_logo


def test_unexpected_amino_acids():
    # Prepare a DataFrame with an unexpected amino acid 'B'
    data = {"A": [0.2, 0.3, 0.1], "B": [0.1, 0.2, 0.3], "C": [0.3, 0.4, 0.1]}
    df = pd.DataFrame(data)

    # Assert ValueError is raised for unexpected amino acid
    with pytest.raises(ValueError) as excinfo:
        Logo(df)

    assert "Unexpected residues in the input data" in str(excinfo.value)


def test_unexpected_nucleotides():
    # Prepare a DataFrame with an unexpected nucleotide 'N'
    data = {"N": [0.2, 0.3, 0.1], "T": [0.1, 0.2, 0.3], "G": [0.3, 0.4, 0.1]}
    df = pd.DataFrame(data)

    # Assert ValueError is raised for unexpected amino acid
    with pytest.raises(ValueError) as excinfo:
        Logo(df, color_scheme=NUCLEOTIDE_COLOR_SCHEME)

    assert "Unexpected residues in the input data" in str(excinfo.value)


@pytest.fixture
def sample_df():
    """Create normalized frequencies for 20 amino acids"""
    np.random.seed(42)
    raw = np.random.rand(20, 12)
    frequencies = pd.DataFrame(raw, index=list("".join(CHEMICAL_COLOR_SCHEME.colors.keys())))
    normalized = frequencies.div(frequencies.sum(axis=0), axis=1).T
    return normalized


def test_valid_input(sample_df: pd.DataFrame):
    fig: go.Figure = Logo(df=sample_df, legend=True, color_scheme=DMS_COLOR_SCHEME, hover=True)
    assert isinstance(fig, Logo)


def test_bar_called_when_hover_false_and_legend_true(sample_df: pd.DataFrame):
    with patch("plotly.graph_objects.Bar") as mock_bar:
        logo = Logo(df=sample_df, hover=False, legend=True)
        assert mock_bar.called, "Expected go.Bar to be called when hover=False and legend=True"
        assert len(logo.traces) > 0, "Expected non-empty traces when legend=True"

        found = any(
            call_args.kwargs.get("x") == [None] and call_args.kwargs.get("y") == [None]
            for call_args in mock_bar.call_args_list
        )
        assert found, "Expected go.Bar to be called with x=[None] and y=[None]"


def test_values_less_than_zero():
    # Prepare a DataFrame with some negative values
    data = {
        "A": [0.2, -0.1, 0.1],
        "C": [0.1, -0.3, 0.2],
        "D": [0.3, 0.4, 0.1],
    }  # Negative value in the 'A' column
    df = pd.DataFrame(data)

    Logo(df)


def test_add_logo_valid(sample_df):
    logo = Logo(df=sample_df, hover=True, legend=True, color_scheme=CHEMICAL_COLOR_SCHEME)
    fig = make_subplots(rows=1, cols=1)

    add_logo(logo, fig, row=1, col=1)

    # Check that traces were added to the figure
    assert len(fig.data) == len(logo.traces), "Expected all logo traces to be added to figure"

    # Check that shapes were added
    assert len(fig.layout.shapes) == len(logo.shapes), "Expected all logo shapes to be added"

    # Check that axis titles were set
    assert fig.layout["xaxis"]["title"]["text"] == logo.xaxis["title"]
    assert fig.layout["yaxis"]["title"]["text"] == logo.yaxis["title"]

    # Check that the legend title was set
    assert fig.layout["legend"]["title"]["text"] == CHEMICAL_COLOR_SCHEME.title


def test_add_logo_invalid_args(sample_df):
    logo = Logo(df=sample_df, hover=False, legend=True)
    fig = make_subplots(rows=1, cols=2)

    with pytest.raises(
        ValueError,
        match="Received rows parameter but not cols.\nrows and cols must be specified together",
    ):
        add_logo(logo, fig, row=1, col=None)
