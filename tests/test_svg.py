import pytest

from plotlylogomaker.svg import PathSegment, Point


def test_valid_M_segment():
    seg = PathSegment("M", [Point(0, 0)])
    assert seg.kind == "M"


def test_valid_L_segment():
    seg = PathSegment("L", [Point(1, 1)])
    assert seg.kind == "L"


def test_valid_Q_segment():
    seg = PathSegment("Q", [Point(0, 0), Point(1, 1)])
    assert seg.kind == "Q"


def test_valid_C_segment():
    seg = PathSegment("C", [Point(0, 0), Point(1, 1), Point(2, 2)])
    assert seg.kind == "C"


def test_valid_Z_segment():
    seg = PathSegment("Z", [])
    assert seg.kind == "Z"


@pytest.mark.parametrize(
    "kind, coords, expected",
    [
        ("M", [], ValueError),
        ("M", [Point(0, 0), Point(1, 1)], ValueError),
        ("M", [0], TypeError),
        ("L", [], ValueError),
        ("L", [Point(0, 0), Point(1, 1)], ValueError),
        ("L", [0], TypeError),
        ("Q", [Point(0, 0)], ValueError),
        ("Q", [Point(0, 0), 0], TypeError),
        ("C", [Point(0, 0), Point(1, 1)], ValueError),
        ("C", [Point(0, 0), Point(1, 1), 0], TypeError),
        ("Z", [Point(0, 0)], TypeError),
        ("A", [], ValueError),
    ],
)
def test_invalid_segments(kind, coords, expected):
    with pytest.raises(expected):
        PathSegment(kind, coords)
