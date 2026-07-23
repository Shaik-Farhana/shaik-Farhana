"""
Render data/contributions.json as a 53-week x 7-day GitHub-style heatmap.

Boxes slide in diagonally (staggered by week + day) using CSS keyframes that
play once on load and then freeze -- no infinite looping "glow". Pure CSS
inside the SVG, so GitHub's <img>-embedded renderer plays it with no JS.
"""

import json
import os
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 28   # room for day-of-week labels
TOP_PAD = 20    # room for month labels
RIGHT_PAD = 14
BOTTOM_PAD = 34  # room for legend + footer

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]
DAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}  # sparse labels like GitHub's own


def build_weeks(days):
    """Group days into weeks (columns), Sunday-first, padding the first
    and last week with None so every column has exactly 7 slots."""
    if not days:
        return []
    parsed = [
        {**d, "dt": datetime.strptime(d["date"], "%Y-%m-%d")} for d in days
    ]
    first = parsed[0]["dt"]
    lead_pad = (first.weekday() + 1) % 7  # weekday(): Mon=0..Sun=6 -> Sun=0
    weeks = []
    week = [None] * lead_pad
    for d in parsed:
        week.append(d)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)
    return weeks


def month_label_positions(weeks):
    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        for day in week:
            if day is None:
                continue
            m = day["dt"].month
            if m != last_month:
                labels.append((wi, MONTH_NAMES[m - 1]))
                last_month = m
            break
    return labels


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    with open(DATA_PATH) as f:
        payload = json.load(f)

    days = payload["days"]
    stats = payload["stats"]
    username = payload["username"]
    weeks = build_weeks(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * CELL + RIGHT_PAD
    height = TOP_PAD + 7 * CELL + BOTTOM_PAD

    boxes = []
    delay_step = 0.008  # seconds per diagonal step, keeps total anim short
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            x = LEFT_PAD + wi * CELL
            y = TOP_PAD + di * CELL
            level = day["level"] if day else 0
            color = PALETTE[level]
            delay = (wi + di) * delay_step
            title = f"{day['date']}: level {level}" if day else ""
            boxes.append(
                f'<rect class="box" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="2" ry="2" fill="{color}" '
                f'style="animation-delay:{delay:.3f}s">'
                + (f"<title>{esc(title)}</title>" if title else "")
                + "</rect>"
            )

    month_labels = [
        f'<text x="{LEFT_PAD + wi * CELL}" y="{TOP_PAD - 7}" '
        f'class="month-label">{name}</text>'
        for wi, name in month_label_positions(weeks)
    ]

    day_labels = [
        f'<text x="{LEFT_PAD - 6}" y="{TOP_PAD + di * CELL + BOX - 1}" '
        f'text-anchor="end" class="day-label">{label}</text>'
        for di, label in DAY_LABELS.items()
    ]

    legend_x = width - RIGHT_PAD - (len(PALETTE) * 14) - 40
    legend_y = height - 18
    legend_boxes = []
    for i, color in enumerate(PALETTE):
        lx = legend_x + 32 + i * 14
        legend_boxes.append(
            f'<rect x="{lx}" y="{legend_y}" width="{BOX}" height="{BOX}" '
            f'rx="2" ry="2" fill="{color}" />'
        )
    legend = (
        f'<text x="{legend_x}" y="{legend_y + BOX - 1}" class="legend-text">Less</text>'
        + "".join(legend_boxes)
        + f'<text x="{legend_x + 32 + len(PALETTE) * 14 + 4}" y="{legend_y + BOX - 1}" '
        f'class="legend-text">More</text>'
    )

    active = stats.get("total_active_days", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    footer_text = (
        f"{active} active days in the last year"
        f" \u00b7 current streak {streak}"
        f" \u00b7 longest streak {longest}"
    )
    footer = (
        f'<text x="{LEFT_PAD}" y="{height - 8}" class="footer-text">'
        f"{esc(footer_text)}</text>"
    )

    svg = f'''<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     xmlns="http://www.w3.org/2000/svg" font-family="'Segoe UI', Helvetica, Arial, sans-serif">
  <style>
    .box {{
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      animation: reveal 0.5s ease-out forwards;
    }}
    @keyframes reveal {{
      0%   {{ opacity: 0; transform: translate(-6px, -6px) scale(0.6); }}
      100% {{ opacity: 1; transform: translate(0, 0) scale(1); }}
    }}
    .month-label, .day-label, .legend-text {{
      fill: #8b949e;
      font-size: 9px;
    }}
    .footer-text {{
      fill: #8b949e;
      font-size: 10px;
    }}
  </style>
  <rect width="100%" height="100%" fill="none" />
  {''.join(month_labels)}
  {''.join(day_labels)}
  {''.join(boxes)}
  {legend}
  {footer}
</svg>
'''

    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote heatmap for {username} -> {OUT_PATH} ({n_weeks} weeks)")


if __name__ == "__main__":
    main()
