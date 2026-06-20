"""
main.py - End-to-end demo: image -> measurements -> draft -> grade -> DXF/SVG.

Run:  python main.py --style dress --out samples/
Produces a graded pattern nest and writes DXF + SVG for the base size.
Runs with zero external dependencies (demo mode); installs in requirements.txt
unlock real CV silhouette extraction.
"""
from __future__ import annotations
import argparse
import json
import os

from src.measure import extract
from src.draft import draft_block
from src.grade import grade_piece
from src.export_cad import to_dxf, to_svg


def run(style: str, image: str | None, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)

    # 1. Computer vision: extract body measurements.
    measurements = extract(image).to_dict()

    # 2. Parametric drafting: measurements -> base pattern block.
    pieces = draft_block(measurements, style=style)

    # 3. Grading: base block -> full size run.
    graded = {p.name: grade_piece(p) for p in pieces}

    # 4. CAD export: write the base (M) size to DXF + SVG.
    base_pieces = [graded[p.name]["M"] for p in pieces]
    dxf = to_dxf(base_pieces, os.path.join(out_dir, f"{style}_M.dxf"))
    svg = to_svg(base_pieces, os.path.join(out_dir, f"{style}_M.svg"))

    summary = {
        "measurements_cm": measurements,
        "style": style,
        "pieces": [p.name for p in pieces],
        "sizes_graded": list(next(iter(graded.values())).keys()),
        "dxf": dxf,
        "svg": svg,
    }
    with open(os.path.join(out_dir, f"{style}_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Fashion pattern AI demo pipeline")
    ap.add_argument("--style", default="dress",
                    choices=["bodice", "skirt", "dress"])
    ap.add_argument("--image", default=None, help="optional silhouette image")
    ap.add_argument("--out", default="samples")
    args = ap.parse_args()
    result = run(args.style, args.image, args.out)
    print(json.dumps(result, indent=2))
