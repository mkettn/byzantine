#!/usr/bin/env python3
"""Command-line tool to generate HTML fasting calendar from YAML config.

Usage:
    fasting-calendar [options] <yaml_file>
    fasting-calendar -h | --help

Options:
    -o <output>       Output HTML file (default: stdout)
    -y <year>         Year to generate calendar for (default: current year)
    --old-style       Use Julian calendar (13-day offset)
    -t <title>        Calendar title
    -l <lang>         Language code: en, de
    -h --help         Show this screen
"""

import sys
import importlib.resources
from docopt import docopt
from byzantine.fastingcalendar import FastingCalendar


def main():
    args = docopt(__doc__)

    try:
        fc = FastingCalendar(args["<yaml_file>"])

        # Get title for the HTML document
        lang = args["-l"] if args["-l"] else "en"
        translation = fc._load_translation(lang)

        if args["-t"]:
            title = args["-t"]
        else:
            title = translation.get("title", "Fasting Calendar")
            if args["--old-style"] and len(translation.get("style", [])) > 0:
                title += f" {translation['style'][0]}"
            elif len(translation.get("style", [])) > 1:
                title += f" {translation['style'][1]}"

        html_tables = fc.to_html(
            year=int(args["-y"]) if args["-y"] else None,
            old_style=args["--old-style"],
            lang=lang,
        )

        # Build full HTML document
        css_content = (
            importlib.resources.files("byzantine.data")
            .joinpath("style.css")
            .read_text()
        )

        html = f"<!DOCTYPE html><html><head><title>{title}</title>"
        html += f"<style>{css_content}</style>"
        html += f"</head><body><h1>{title}</h1>{html_tables}</body></html>"

        if args["-o"]:
            with open(args["-o"], "w") as f:
                f.write(html)
            print(f"Written to {args['-o']}")
        else:
            print(html)

    except FileNotFoundError:
        print(f"Error: YAML file not found: {args['<yaml_file>']}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
