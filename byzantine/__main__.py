#!/usr/bin/env python3
"""Command-line tool to generate HTML fasting calendar from YAML config."""

import argparse
import sys
from byzantine.fastingcalendar import FastingCalendar


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML fasting calendar from YAML config"
    )
    parser.add_argument(
        "yaml_file",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output HTML file (default: stdout)",
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        help="Year to generate calendar for (default: current year)",
    )
    parser.add_argument(
        "--old-style",
        action="store_true",
        help="Use Julian calendar (13-day offset)",
    )
    parser.add_argument(
        "-t",
        "--title",
        default="Fasting Calendar",
        help="Calendar title",
    )

    args = parser.parse_args()

    try:
        fc = FastingCalendar(args.yaml_file)
        html = fc.to_html(
            year=args.year,
            old_style=args.old_style,
            title=args.title,
        )

        if args.output:
            with open(args.output, "w") as f:
                f.write(html)
            print(f"Written to {args.output}")
        else:
            print(html)

    except FileNotFoundError:
        print(f"Error: YAML file not found: {args.yaml_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
