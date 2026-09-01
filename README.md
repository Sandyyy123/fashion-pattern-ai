> **⚠️ Proprietary — All Rights Reserved.** © 2026 Sandeep Grover. This repository is licensed to Sandeep Grover and may **not** be used, run, copied, modified, distributed, or used to train models without prior written permission. Public visibility does not grant a license. See [LICENSE](LICENSE).

---

# fashion-pattern-ai

A runnable reference pipeline for **AI-assisted garment patternmaking** -
the core loop behind an automated fashion-production platform: a photo or design
brief in, a graded, CAD-ready pattern set out.

This is a demonstration architecture built for an Upwork technical-lead engagement.
It runs end-to-end with **zero external dependencies** (deterministic demo mode)
and unlocks real computer vision + LLM parsing when the optional deps are installed.

## Pipeline

```
 design brief ─┐
               ├─►  [1] design_assistant  (LLM brief → structured spec)
   photo ──────┘
        │
        ▼
   [2] measure.py   (CV silhouette/keypoints → body measurements, cm)
        │
        ▼
   [3] draft.py     (parametric flat-pattern drafting → base block)
        │
        ▼
   [4] grade.py     (grade rules → full size run XS–XL)
        │
        ▼
   [5] export_cad.py  (→ DXF R12 + SVG, read by Gerber/Optitex/CLO/Browzwear)
```

| Stage | File | What it does |
|-------|------|--------------|
| 1 | `src/design_assistant.py` | NL brief → `{style, ease, size_run, notes}` (Claude or rule-based) |
| 2 | `src/measure.py` | Image/keypoints → 7 standard body measurements via elliptical girth model |
| 3 | `src/draft.py` | Measurements → 2D pattern pieces (bodice / skirt / dress blocks) |
| 4 | `src/grade.py` | Base block → graded nest across a size run |
| 5 | `src/export_cad.py` | Pieces → universal DXF + SVG for any CAD seat |

## Run

```bash
python main.py --style dress --out samples/
# writes samples/dress_M.dxf, dress_M.svg, dress_summary.json
```

With a silhouette image:

```bash
python main.py --style dress --image path/to/front.jpg --out samples/
```

Design brief → spec:

```bash
python -m src.design_assistant
```

## Why DXF R12

Every industry CAD seat (Gerber AccuMark, Lectra Modaris, Optitex, CLO3D,
Browzwear VStitcher) imports R12 ASCII DXF. Writing it directly (no proprietary
SDK) keeps the platform CAD-agnostic and avoids per-seat licensing lock-in.

## Production roadmap (what the MVP build adds)

- Replace the demo keypoint hook in `measure.py` with a trained pose +
  segmentation model (mediapipe / SAM) and reference-object auto-calibration.
- Curve fitting (Bézier) on necklines/armholes/sleeve caps instead of polylines.
- Dart placement + true-up, seam allowance offsetting, notch/grain annotation.
- Marker-making + nesting for fabric-efficient cut layouts.
- 3D drape preview via CLO/Browzwear API for fit validation before sampling.

---
Dr. Sandeep Grover — PhD Data Science. Built as a working sample, not a stub.
