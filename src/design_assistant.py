"""
design_assistant.py - LLM design-brief -> structured spec.

Turns a natural-language design brief ("fitted midi dress, cap sleeve, size run
XS-XL, cotton poplin") into a structured spec the drafting engine can consume:
style, ease, size run, notes. Uses the Anthropic Claude API when ANTHROPIC_API_KEY
is set; otherwise a deterministic rule-based parser keeps the pipeline runnable.
"""
from __future__ import annotations
import os
import json
import re

STYLE_KEYWORDS = {
    "dress": ["dress", "frock", "gown"],
    "skirt": ["skirt"],
    "bodice": ["top", "blouse", "bodice", "shirt"],
}
EASE_BY_FIT = {"fitted": 4.0, "regular": 6.0, "relaxed": 10.0, "oversized": 16.0}


def _rule_based(brief: str) -> dict:
    b = brief.lower()
    style = next((s for s, kws in STYLE_KEYWORDS.items()
                  if any(k in b for k in kws)), "dress")
    fit = next((f for f in EASE_BY_FIT if f in b), "regular")
    sizes = re.findall(r"\b(xs|s|m|l|xl|xxl)\b", b)
    return {
        "style": style,
        "ease_cm": EASE_BY_FIT[fit],
        "size_run": [s.upper() for s in sizes] or ["XS", "S", "M", "L", "XL"],
        "notes": brief.strip(),
        "source": "rule_based",
    }


def parse_brief(brief: str) -> dict:
    """Use Claude if available; otherwise fall back to the rule-based parser."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return _rule_based(brief)
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": (
                    "Extract a JSON pattern spec from this design brief. "
                    "Keys: style (dress|skirt|bodice), ease_cm (number), "
                    "size_run (list), notes (string). Brief: " + brief
                ),
            }],
        )
        text = msg.content[0].text
        spec = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
        spec["source"] = "claude"
        return spec
    except Exception:
        return _rule_based(brief)


if __name__ == "__main__":
    print(json.dumps(parse_brief(
        "fitted midi dress, cap sleeve, size run XS-XL, cotton poplin"),
        indent=2))
