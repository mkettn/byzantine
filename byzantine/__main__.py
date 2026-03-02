#!/usr/bin/env python3
"""Command-line tool to generate HTML fasting calendar from YAML config.

Usage:
    fasting-calendar [options] <yaml_file> 
    fasting-calendar -h | --help

Options:
    -o <output>       Output HTML file (default: stdout)
    -y <year>         Year to generate calendar for (default: current year)
    --old-style       Use Julian calendar (13-day offset)
    -t <title>        Calendar title [default: Fasting Calendar]
    -h --help         Show this screen
"""

import sys
from docopt import docopt
from byzantine.fastingcalendar import FastingCalendar


def main():
    args = docopt(__doc__)

    try:
        fc = FastingCalendar(args["<yaml_file>"])
        html = fc.to_html(
            year=int(args["-y"]) if args["-y"] else None,
            old_style=args["--old-style"],
            title=args["-t"],
        )

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
