"""
grade.py - Size grading of a base pattern across a size run.

Applies incremental grade rules (per-point x/y deltas) to a base piece to
generate a full size set. Grade increments follow standard girth grading:
~4cm bust/hip and ~3cm waist per size step, distributed across the quarter
pattern. This is the step that turns one sample block into a production-ready
graded nest.
"""
from __future__ import annotations
from copy import deepcopy

# Default size run and the body-girth steps between them (cm, full body).
DEFAULT_SIZES = ["XS", "S", "M", "L", "XL"]
GIRTH_STEP_CM = 4.0  # bust/hip per size; quarter-pattern delta = /4


def _grade_delta(size_index: int, base_index: int) -> float:
    """Quarter-pattern x-grow per size step relative to the base size."""
    return (size_index - base_index) * (GIRTH_STEP_CM / 4.0)


def grade_piece(piece, sizes=None, base="M") -> dict:
    """
    Return {size: graded_piece}. Width-bearing points (x>0) grow outward by the
    grade delta; centre-front points (x==0) stay anchored. Length grows a
    smaller 1cm/size to keep proportions realistic.
    """
    sizes = sizes or DEFAULT_SIZES
    base_index = sizes.index(base)
    graded = {}
    for i, size in enumerate(sizes):
        dx = _grade_delta(i, base_index)
        dy = (i - base_index) * 1.0
        g = deepcopy(piece)
        new_pts = []
        for (x, y) in g.points:
            nx = x + dx if x > 0.01 else x
            ny = y - dy if y < -0.01 else y  # lengths are negative downward
            new_pts.append((round(nx, 2), round(ny, 2)))
        g.points = new_pts
        g.name = f"{piece.name}_{size}"
        graded[size] = g
    return graded


if __name__ == "__main__":
    from draft import bodice_front
    demo = {"bust": 92.0, "waist": 74.0, "hip": 98.0,
            "nape_to_waist": 41.0, "shoulder": 39.0,
            "arm_length": 58.0, "inseam": 78.0}
    nest = grade_piece(bodice_front(demo))
    for size, piece in nest.items():
        print(size, piece.points[2])  # side-waist point moves outward per size
