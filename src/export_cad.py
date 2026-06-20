"""
export_cad.py - Write pattern pieces to DXF and SVG.

DXF (R12 ASCII) is the universal interchange format every CAD seat reads -
Gerber AccuMark, Optitex, Lectra, CLO3D, Browzwear. SVG is for quick visual
QC. No third-party CAD libs required: R12 DXF is plain text, written directly.
"""
from __future__ import annotations


def _dxf_polyline(points: list[tuple[float, float]], layer: str) -> str:
    out = ["0", "POLYLINE", "8", layer, "66", "1", "70", "1"]
    for (x, y) in points:
        out += ["0", "VERTEX", "8", layer, "10", f"{x:.3f}", "20", f"{y:.3f}"]
    out += ["0", "SEQEND"]
    return "\n".join(out)


def to_dxf(pieces, path: str) -> str:
    """Write one or more Piece objects to an R12 DXF file."""
    body = ["0", "SECTION", "2", "ENTITIES"]
    for p in pieces:
        body.append(_dxf_polyline(p.points + [p.points[0]], p.name))
        if p.grainline:
            (x1, y1), (x2, y2) = p.grainline
            body += ["0", "LINE", "8", f"{p.name}_grain",
                     "10", f"{x1:.3f}", "20", f"{y1:.3f}",
                     "11", f"{x2:.3f}", "21", f"{y2:.3f}"]
    body += ["0", "ENDSEC", "0", "EOF"]
    text = "\n".join(body) + "\n"
    with open(path, "w") as fh:
        fh.write(text)
    return path


def to_svg(pieces, path: str, scale: float = 4.0) -> str:
    """Quick SVG render for visual QC (y flipped so up is up)."""
    xs = [x for p in pieces for (x, y) in p.points]
    ys = [y for p in pieces for (x, y) in p.points]
    w = (max(xs) - min(xs) + 20) * scale
    h = (max(ys) - min(ys) + 20) * scale
    ox, oy = -min(xs) + 10, -min(ys) + 10
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" '
             f'height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}">']
    for p in pieces:
        pts = " ".join(f"{(x+ox)*scale:.1f},{h-(y+oy)*scale:.1f}"
                       for (x, y) in p.points + [p.points[0]])
        parts.append(f'<polygon points="{pts}" fill="none" '
                     f'stroke="#6c5ce7" stroke-width="1.5"/>')
    parts.append("</svg>")
    text = "\n".join(parts)
    with open(path, "w") as fh:
        fh.write(text)
    return path
