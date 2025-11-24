#!/usr/bin/env python3
"""
Simple countdown timer that lets you specify the duration in minutes.

Usage:
    python timer.py --minutes 1.5

The script will count down the specified duration and notify when time is up.
"""

import argparse
import sys
import time
from typing import Final

SECONDS_PER_MINUTE: Final[int] = 60


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Countdown timer in minutes")
    parser.add_argument(
        "--minutes",
        type=float,
        default=1.0,
        help="Timer duration in minutes (can be a decimal)",
    )
    return parser.parse_args(argv)


def format_time(seconds_remaining: int) -> str:
    minutes, seconds = divmod(seconds_remaining, SECONDS_PER_MINUTE)
    return f"{minutes:02d}:{seconds:02d}"


def countdown(total_seconds: int) -> None:
    for remaining in range(total_seconds, -1, -1):
        print(f"\rTime left: {format_time(remaining)}", end="", flush=True)
        if remaining > 0:
            time.sleep(1)
    print("\nTime's up!")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.minutes <= 0:
        print("Please provide a positive number of minutes.", file=sys.stderr)
        return 1

    total_seconds = int(args.minutes * SECONDS_PER_MINUTE)
    print(f"Starting a {args.minutes:.2f}-minute timer...")
    countdown(total_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
