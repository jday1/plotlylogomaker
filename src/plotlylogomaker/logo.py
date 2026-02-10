"""Defines the Logo class for generating Plotly-based sequence logos."""

from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.basedatatypes import _is_select_subplot_coordinates_arg
from plotly.graph_objs import layout

from plotlylogomaker.color import CHEMICAL_COLOR_SCHEME, ColorScheme
from plotlylogomaker.svg import SVG_DEFINITIONS, SVGPath


class Logo:
    """Generate the traces and shapes for a Plotly-based Sequence logo."""

    def __init__(
        self,
        df: pd.DataFrame,
        color_scheme: ColorScheme = CHEMICAL_COLOR_SCHEME,
        hover: bool = True,
        legend: bool = True,
        reflect_negative_symbols: bool = True,
    ) -> None:
        """Initialize the Logo object with the input dataframe and configuration options.

        Args:
        df (pd.DataFrame):
            The preprocessed input dataframe. Row indices are sequence positions and columns are residues.
            Values are relative frequencies or scores. All residues do not need to be specified in the columns.
        color_scheme (ColorScheme):
            The color scheme to use, by default uses the CHEMICAL_COLOR_SCHEME.
        hover (bool):
            Whether to include information when hovering over the logo for interactive inspection.
        legend (bool):
            Whether to include a legend in the plot illustrating the categories for the ColorScheme.
        reflect_negative_symbols (bool):
            Whether to reflect the negative symbols in the logo. If True, the negative symbols will be reflected
            vertically. True by default.

        """
        self.df = df
        self._positions = len(self.df)
        self.color_scheme = color_scheme
        self.hover = hover
        self.paths: list[tuple[str, str]] = []
        self.residues = np.array(list(color_scheme.valid_keys))
        self.traces: list[go.Bar] = []
        self.shapes: list[dict] = []
        self.legend = legend
        self.x_adjustment = 0.01
        self.y_adjustment = 0.005
        self.inverted_negative_symbols = reflect_negative_symbols

        unexpected_residues = set(df.columns) - color_scheme.valid_keys
        if unexpected_residues:
            raise ValueError(f"Unexpected residues in the input data: {unexpected_residues}.")

        min_y, max_y = self.add_shapes_and_traces()

        # Axis config (to be reused in subplots)
        self.xaxis = dict(
            dtick=1,
            title="Position",
            range=[0.5, self._positions + 0.5],
            fixedrange=False,
        )
        self.yaxis = dict(
            title="Frequency",
            range=[min_y, max_y],
            fixedrange=True,
        )

        if self.legend:
            for _, color in self.color_scheme.colors.items():
                self.traces.append(
                    go.Bar(x=[None], y=[None], marker_color=color.hex, name=color.name)
                )

    def add_shapes_and_traces(self) -> tuple[float, float]:
        """Add shapes and traces to the logo based on the input dataframe."""
        min_y, max_y = 0.0, 0.0
        x = 0.5
        width = 1

        for idx in self.df.index:
            t: pd.Series = self.df.loc[idx, :]

            positive_t = t[t > 0].sort_values()
            last_top = 0.0

            for aa, freq in positive_t.items():
                if freq > 0:
                    self.add_shape(
                        aa,
                        x + self.x_adjustment,
                        x + width - self.x_adjustment,
                        last_top + freq,
                        last_top + self.y_adjustment,
                    )

                last_top += freq
                max_y = max(max_y, last_top)

            if self.hover:
                self.add_trace(idx, positive_t)

            negative_t = t[t < 0].sort_values(ascending=False)
            last_bottom = 0.0

            for aa, freq in negative_t.items():
                kwargs: dict[str, Any] = {
                    "letter": aa,
                    "left": x + self.x_adjustment,
                    "right": x + width - self.x_adjustment,
                }

                if self.inverted_negative_symbols:
                    kwargs["top"] = last_bottom + freq
                    kwargs["bottom"] = last_bottom - self.y_adjustment
                else:
                    kwargs["top"] = last_bottom - self.y_adjustment
                    kwargs["bottom"] = last_bottom + freq

                self.add_shape(**kwargs)

                last_bottom += freq

                min_y = min(min_y, last_bottom)

            x += width

            if self.hover:
                self.add_trace(idx, negative_t)

        return min_y - self.y_adjustment, max_y + self.y_adjustment

    def add_shape(self, letter: str, left: float, right: float, top: float, bottom: float) -> None:
        """Add a shape to the logo for a given letter and position."""
        path = SVGPath(SVG_DEFINITIONS[letter])
        path.invert("y")
        path.reposition(left=left, right=right, bottom=bottom, top=top)
        self.shapes.append(
            dict(
                type="path",
                path=str(path),
                ysizemode="scaled",
                xsizemode="scaled",
                fillcolor=self.color_scheme.hex_lookup[letter],
                line_color=self.color_scheme.hex_lookup[letter],
                opacity=0.9,
                line_width=1,
            )
        )

    def add_trace(self, idx: int, series: pd.Series) -> None:
        """Add a trace to the logo for a given position and series of frequencies."""
        self.traces.append(
            go.Bar(
                x=[idx + 1] * len(series),
                y=series,
                hovertemplate="Position %{x}<br>Letter %{customdata[0]}<br>Frequency %{value}<extra></extra>",
                showlegend=False,
                customdata=pd.DataFrame(series.index),
                width=1,
                opacity=0.0,  # Makes the bars transparent.
                marker=dict(color="rgba(0,0,0,0)"),  # Makes the hoverinfo background transparent.
            )
        )


def make_shape(
    arg: Any | None = None,  # noqa: ANN401
    editable: Any | None = None,  # noqa: ANN401
    fillcolor: Any | None = None,  # noqa: ANN401
    fillrule: Any | None = None,  # noqa: ANN401
    label: Any | None = None,  # noqa: ANN401
    layer: Any | None = None,  # noqa: ANN401
    legend: Any | None = None,  # noqa: ANN401
    legendgroup: Any | None = None,  # noqa: ANN401
    legendgrouptitle: Any | None = None,  # noqa: ANN401
    legendrank: Any | None = None,  # noqa: ANN401
    legendwidth: Any | None = None,  # noqa: ANN401
    line: Any | None = None,  # noqa: ANN401
    name: Any | None = None,  # noqa: ANN401
    opacity: Any | None = None,  # noqa: ANN401
    path: Any | None = None,  # noqa: ANN401
    showlegend: Any | None = None,  # noqa: ANN401
    templateitemname: Any | None = None,  # noqa: ANN401
    type: Any | None = None,  # noqa: ANN401
    visible: Any | None = None,  # noqa: ANN401
    x0: Any | None = None,  # noqa: ANN401
    x0shift: Any | None = None,  # noqa: ANN401
    x1: Any | None = None,  # noqa: ANN401
    x1shift: Any | None = None,  # noqa: ANN401
    xanchor: Any | None = None,  # noqa: ANN401
    xref: Any | None = None,  # noqa: ANN401
    xsizemode: Any | None = None,  # noqa: ANN401
    y0: Any | None = None,  # noqa: ANN401
    y0shift: Any | None = None,  # noqa: ANN401
    y1: Any | None = None,  # noqa: ANN401
    y1shift: Any | None = None,  # noqa: ANN401
    yanchor: Any | None = None,  # noqa: ANN401
    yref: Any | None = None,  # noqa: ANN401
    ysizemode: Any | None = None,  # noqa: ANN401
    **kwargs: dict[str, Any],
) -> layout.Shape:
    """Create a shape object for Plotly figures.

    It replicates the logic in the plotly.graph_objects._figure.Figure.add_shape method to create a layout.Shape object
    but just returns the object rather than making a subsequent call. Instead, the returned objects are passed as a list
    to the add_shapes function which handles the addition of multiple shapes to the figure.

    This function uses very generous typing to comply with mypy as the underlying method is not type-annotated.
    """
    new_obj = layout.Shape(
        arg,
        editable=editable,
        fillcolor=fillcolor,
        fillrule=fillrule,
        label=label,
        layer=layer,
        legend=legend,
        legendgroup=legendgroup,
        legendgrouptitle=legendgrouptitle,
        legendrank=legendrank,
        legendwidth=legendwidth,
        line=line,
        name=name,
        opacity=opacity,
        path=path,
        showlegend=showlegend,
        templateitemname=templateitemname,
        type=type,
        visible=visible,
        x0=x0,
        x0shift=x0shift,
        x1=x1,
        x1shift=x1shift,
        xanchor=xanchor,
        xref=xref,
        xsizemode=xsizemode,
        y0=y0,
        y0shift=y0shift,
        y1=y1,
        y1shift=y1shift,
        yanchor=yanchor,
        yref=yref,
        ysizemode=ysizemode,
        **kwargs,
    )

    return new_obj


def add_shapes(
    fig: go.Figure,
    prop_singular: str,
    prop_plural: str,
    new_objs: list[layout.Shape],
    row: int | None = None,
    col: int | None = None,
    secondary_y: bool | None = None,
    exclude_empty_subplots: bool = False,
) -> go.Figure:
    """Add multiple shapes to the same figure.

    This was introduced because plotly.graph_objects.Figure.add_shape only adds a single shape at a time
    which is costly in terms of performance.

    This add_shapes function is derived from plotly.basedatatypes.BaseFigure._add_annotation_like but uses a list of shapes
    (new_objs) rather than a single obj as the original method does. To account for this, this function introduces checks to
    ensure that the axes references are consistent across all shapes given in new_objs.
    """
    yrefs = {new_obj.yref for new_obj in new_objs}
    if len(yrefs) > 1:
        raise ValueError("Cannot add shapes to multiple yrefs at once.\n")
    yref = yrefs.pop()

    # Make sure we have both row and col or neither
    if row is not None and col is None:
        raise ValueError(
            "Received row parameter but not col.\nrow and col must be specified together"
        )
    elif col is not None and row is None:
        raise ValueError(
            "Received col parameter but not row.\nrow and col must be specified together"
        )

    # Address multiple subplots
    if row is not None and _is_select_subplot_coordinates_arg(row, col):
        # TODO product argument could be added
        rows_cols = fig._select_subplot_coordinates(row, col)
        for r, c in rows_cols:
            add_shapes(
                fig,
                prop_singular,
                prop_plural,
                new_objs,
                row=r,
                col=c,
                secondary_y=secondary_y,
                exclude_empty_subplots=exclude_empty_subplots,
            )
        return fig

    # Get grid_ref if specific row or column requested
    # Checking col is not None is superfluous due to earlier checks but makes type checking easier.
    if row is not None and col is not None:
        grid_ref = fig._validate_get_grid_ref()
        if row > len(grid_ref):
            raise IndexError(
                f"row index {row} out-of-bounds, row index must be between 1 and {len(grid_ref)}, inclusive."
            )
        if col > len(grid_ref[row - 1]):
            raise IndexError(
                f"column index {col} out-of-bounds, column index must be between 1 and {len(grid_ref[row - 1])}, inclusive."
            )
        refs = grid_ref[row - 1][col - 1]
        if not refs:
            raise ValueError(f"No subplot found at position ({row}, {col})")

        if refs[0].subplot_type != "xy":
            raise ValueError(
                f"""
Cannot add {prop_singular} to subplot at position ({row}, {col}) because subplot
is of type {refs[0].subplot_type}."""
            )

        # If the new_object was created with a yref specified that did not include paper or domain,
        # the specified yref should be used otherwise assign the xref and yref from the layout_keys
        if yref is None or yref == "y" or "paper" in yref or "domain" in yref:
            if len(refs) == 1 and secondary_y:
                raise ValueError(
                    f"""
Cannot add {prop_singular} to secondary y-axis of subplot at position ({row}, {col})
because subplot does not have a secondary y-axis"""
                )
            if secondary_y:
                xaxis, yaxis = refs[1].layout_keys
            else:
                xaxis, yaxis = refs[0].layout_keys
            xref, yref = xaxis.replace("axis", ""), yaxis.replace("axis", "")
        else:
            yref = yref
            xaxis = refs[0].layout_keys[0]
            xref = xaxis.replace("axis", "")
        # if exclude_empty_subplots is True, check to see if subplot is
        # empty and return if it is
        if exclude_empty_subplots and (
            not fig._subplot_not_empty(xref, yref, selector=bool(exclude_empty_subplots))
        ):
            return fig

        # in case the user specified they wanted an axis to refer to the
        # domain of that axis and not the data, append ' domain' to the
        # computed axis accordingly
        def _add_domain(ax_letter: str, new_axref: str) -> str:
            axref = ax_letter + "ref"

            axrefs_present = {
                axref in new_obj._props.keys() and "domain" in new_obj[axref]
                for new_obj in new_objs
            }
            if len(axrefs_present) > 1:
                raise ValueError("axref_present must be the same for all shapes")
            axref_domain_present = axrefs_present.pop()

            if axref_domain_present:
                new_axref += " domain"
            return new_axref

        xref, yref = map(lambda t: _add_domain(*t), zip(["x", "y"], [xref, yref]))

        for new_obj in new_objs:
            new_obj.update(xref=xref, yref=yref)

    fig.layout[prop_plural] += tuple(new_objs)

    for new_obj in new_objs:
        new_obj.update(xref=None, yref=None)

    return fig


def add_logo(logo: Logo, fig: go.Figure, row: int | None = None, col: int | None = None) -> None:
    """Add a logo to a Plotly figure."""
    # Add all traces for this logo
    if logo.traces:
        fig.add_traces(logo.traces, rows=row, cols=col)
        fig.update_layout(barmode="relative")

    new_objs: list[layout.Shape] = [make_shape(**shape.copy()) for shape in logo.shapes]
    add_shapes(fig, "shape", "shapes", new_objs, row=row, col=col)

    # Update x and y axes for this subplot
    fig.update_xaxes(logo.xaxis, row=row, col=col)
    fig.update_yaxes(logo.yaxis, row=row, col=col)

    if logo.legend:
        fig.update_layout(
            legend_title=logo.color_scheme.title,
            legend_itemclick=False,
            legend_itemdoubleclick=False,
        )
