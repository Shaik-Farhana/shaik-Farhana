"""
Fetch a GitHub user's public contribution calendar (no token, no GraphQL).

GitHub serves the same calendar fragment the profile page uses at:
    https://github.com/users/<username>/contributions

We scrape the day cells with BeautifulSoup and write data/contributions.json
containing the raw days plus a few derived stats (current streak, longest
streak, best day, monthly totals) that the renderer and info card can use.
"""

import json
import os
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "Shaik-Farhana")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # Each day is a <td> with a data-date and a data-level (0-4) attribute,
    # or an <li>/<rect> depending on GitHub's current markup revision — we
    # check both shapes defensively.
    cells = soup.select("td.ContributionCalendar-day") or soup.select(
        "[data-date][data-level]"
    )
    for cell in cells:
        d = cell.get("data-date")
        level = cell.get("data-level")
        if d is None or level is None:
            continue
        days.append({"date": d, "level": int(level)})

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days):
    if not days:
        return {
            "total": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": None,
            "monthly": {},
        }

    # level -> approximate contribution count isn't exposed publicly, so we
    # treat "level > 0" as "contributed that day" for streaks, and report
    # level totals for the legend / footer text.
    total_active_days = sum(1 for d in days if d["level"] > 0)

    longest_streak = 0
    current_run = 0
    for d in days:
        if d["level"] > 0:
            current_run += 1
            longest_streak = max(longest_streak, current_run)
        else:
            current_run = 0

    # current streak = trailing run ending today (or yesterday, since today
    # may not be finished yet)
    current_streak = 0
    for d in reversed(days):
        if d["level"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days, key=lambda x: x["level"])

    monthly = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + (1 if d["level"] > 0 else 0)

    return {
        "total_active_days": total_active_days,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
    }


def main():
    days = fetch_days()
    stats = derive_stats(days)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {len(days)} days -> {OUT_PATH}")


if __name__ == "__main__":
    main()
