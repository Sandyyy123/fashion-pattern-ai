"""
draft.py - Parametric block (sloper) drafting from measurements.

Turns a Measurements record into 2D pattern pieces (ordered point polylines)
using classic flat-pattern drafting maths - the same construction a pattern
cutter does by hand, expressed as parametric geometry. Outputs pieces that the
exporter writes to DXF/SVG for any CAD seat (Gerber, Optitex, CLO, Browzwear).
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Piece:
    name: str
    # ordered (x, y) cm points, closed polyline
    points: list[tuple[float, float]] = field(default_factory=list)
    grainline: tuple[tuple[float, float], tuple[float, float]] | None = None
    seam_allowance_cm: float = 1.0


def bodice_front(m: dict, ease_cm: float = 6.0) -> Piece:
    """
    Draft a front bodice block. Width = quarter bust + ease share;
    height = nape-to-waist. Neckline + armhole are simple curve approximations
    (control points), sufficient for a graded sample block.
    """
    quarter = m["bust"] / 4.0 + ease_cm / 4.0
    h = m["nape_to_waist"]
    shoulder = m["shoulder"] / 2.0
    neck_w = m["bust"] / 20.0 + 2.0
    neck_d = neck_w + 1.0

    pts = [
        (0.0, 0.0),                 # centre-front neck
        (0.0, -h),                  # centre-front waist
        (quarter, -h),              # side waist
        (quarter, -h + h * 0.55),   # underarm
        (shoulder, -neck_d - 1.0),  # shoulder tip
        (neck_w, 0.0),              # neck shoulder point
    ]
    return Piece(
        name="bodice_front",
        points=pts,
        grainline=((0.0, -1.0), (0.0, -h + 1.0)),
    )


def skirt_front(m: dict, length_cm: float = 60.0, ease_cm: float = 4.0) -> Piece:
    """Straight skirt front block: quarter hip + ease, dart intake at waist."""
    quarter_hip = m["hip"] / 4.0 + ease_cm / 4.0
    quarter_waist = m["waist"] / 4.0 + 1.0  # +1 dart allowance
    pts = [
        (0.0, 0.0),
        (0.0, -length_cm),
        (quarter_hip, -length_cm),
        (quarter_hip, -18.0),       # hip line
        (quarter_waist, 0.0),
    ]
    return Piece(
        name="skirt_front",
        points=pts,
        grainline=((0.0, -1.0), (0.0, -length_cm + 1.0)),
    )


def draft_block(measurements: dict, style: str = "bodice") -> list[Piece]:
    """Dispatch by style; returns the pattern pieces for that garment block."""
    if style == "bodice":
        return [bodice_front(measurements)]
    if style == "skirt":
        return [skirt_front(measurements)]
    if style == "dress":
        return [bodice_front(measurements), skirt_front(measurements)]
    raise ValueError(f"unknown style: {style}")


if __name__ == "__main__":
    demo = {"bust": 92.0, "waist": 74.0, "hip": 98.0,
            "nape_to_waist": 41.0, "shoulder": 39.0,
            "arm_length": 58.0, "inseam": 78.0}
    for p in draft_block(demo, "dress"):
        print(p.name, "->", len(p.points), "points")
