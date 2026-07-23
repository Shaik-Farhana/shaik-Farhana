"""
Hand-author a neofetch-style info card: a title bar, then colored key/value
rows (Now, Prev, Stack, Highlights). Each line fades + slides in on a short
stagger so it looks like it's printing. Set STATIC=1 to emit a frozen frame
(useful for local Quick Look previews where SMIL/CSS animation won't play).

Edit CONTENT below whenever your role, stack, or highlights change --
this file is static and only needs re-running by hand, not by the daily cron.
"""

import os

USERNAME = "Shaik-Farhana"

CONTENT = {
    "now": "Final-year B.E. CSE (Data Science)",
    "prev": "IBM Agentic AI \u00b7 Google Gen AI Academy APAC",
    "stack": "React \u00b7 FastAPI \u00b7 Python \u00b7 LangGraph \u00b7 Groq/Gemini",
    "highlights": "Team Deccans \u2014 ISRO BAH 2026 finalist (PS13)",
}

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

WIDTH = 490
LINE_H = 30
TOP_PAD = 44
ROWS = [
    ("Now", CONTENT["now"], "#39d353"),
    ("Prev", CONTENT["prev"], "#58a6ff"),
    ("Stack", CONTENT["stack"], "#f2cc60"),
    ("Highlights", CONTENT["highlights"], "#d2a8ff"),
]
HEIGHT = TOP_PAD + LINE_H * len(ROWS) + 24


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    is_static = os.environ.get("STATIC") == "1"

    rows_svg = []
    for i, (label, value, color) in enumerate(ROWS):
        y = TOP_PAD + i * LINE_H
        delay = i * 0.18
        anim_class = "" if is_static else "row"
        style = "" if is_static else f'style="animation-delay:{delay:.2f}s"'
        rows_svg.append(
            f'<g class="{anim_class}" {style}>'
            f'<text x="24" y="{y}" class="label" fill="{color}">{esc(label)}</text>'
            f'<text x="150" y="{y}" class="value">{esc(value)}</text>'
            f"</g>"
        )

    style_block = (
        ""
        if is_static
        else """
    .row { opacity: 0; transform: translateX(-6px); animation: printin 0.4s ease-out forwards; }
    @keyframes printin { to { opacity: 1; transform: translateX(0); } }
    """
    )

    svg = f'''<svg viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}"
     xmlns="http://www.w3.org/2000/svg" font-family="'Cascadia Code','Fira Code',monospace">
  <style>
    .titlebar {{ fill: #8b949e; font-size: 11px; }}
    .dot {{ }}
    .label {{ font-size: 13px; font-weight: bold; }}
    .value {{ font-size: 13px; fill: #c9d1d9; }}
    {style_block}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="8" ry="8"
        fill="#0d1117" stroke="#30363d" />
  <circle class="dot" cx="20" cy="18" r="5" fill="#ff5f56" />
  <circle class="dot" cx="38" cy="18" r="5" fill="#ffbd2e" />
  <circle class="dot" cx="56" cy="18" r="5" fill="#27c93f" />
  <text x="{WIDTH / 2}" y="22" text-anchor="middle" class="titlebar">{esc(USERNAME)}@github: neofetch</text>
  <line x1="0" y1="32" x2="{WIDTH}" y2="32" stroke="#30363d" />
  {''.join(rows_svg)}
</svg>
'''

    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {'static' if is_static else 'animated'} info card -> {OUT_PATH}")


if __name__ == "__main__":
    main()
