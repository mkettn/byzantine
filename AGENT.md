# Agent Guidelines for byzantine

## Project Overview

Orthodox fasting calendar library and CLI tool that generates HTML calendars from YAML configuration.

## Key Files

- `byzantine/day.py` - `Day` class for parsing date strings (MMDD, e+Nd, e-Nw, etc.)
- `byzantine/fastingcalendar.py` - `FastingCalendar` class for loading YAML and generating HTML
- `byzantine/__main__.py` - CLI entry point using docopt
- `byzantine/data/style.css` - CSS for HTML calendar rendering
- `byzantine/data/lang/` - Translation files (de.yml, en.yml)
- `fastingcalendar.yml` - Fasting rules configuration

## Important Design Decisions

### Date String Format (Day class)
- `"MMDD"` - Fixed solar date (e.g., "0612" = June 12)
- `"e[+-]N[d|w]"` - Days/weeks relative to Orthodox Easter (e.g., "e+50d", "e-3w")
- `"e[+-]N[d|w][>|>]weekday"` - Adjust to next/previous weekday

### YAML Format
- Fixed dates: `"MMDD": "name"` or `"MMDD": {name: "...", rule: "no_fish"}`
- Easter-relative: `"e+39": "Ascension"`
- Ranges: `"MMDD..MMDD": { weekday: rule, ... }`
- Weekday shortcuts: `mon..sun`, `sat..sun`, `wed,fri`

### Fasting Rules (from YAML)
- `no_fast` - Everything allowed
- `no_meat` - No meat, dairy, eggs
- `no_dairy` - No dairy, eggs, fish
- `no_fish` - No fish
- `no_oil` - No oil

### Old Style (Julian Calendar)
- When `old_style=True`, a 13-day offset is applied to fixed dates
- Easter-relative dates (starting with 'e') are NOT offset
- The code processes both the target year and previous year to handle dates that shift into the target year

### HTML Generation
- Default language is English ("en")
- CSS classes use rule names: `no_meat`, `no_dairy`, `no_fish`, `no_oil`
- Legend is rendered outside the 3-column month grid

## Testing

Run tests with: `pytest`

## CLI Usage

```bash
fasting-calendar [options] <yaml_file>

Options:
  -o <output>       Output HTML file (default: stdout)
  -y <year>         Year to generate calendar for (default: current year)
  --old-style       Use Julian calendar (13-day offset)
  -t <title>        Calendar title
```

## Common Issues

1. **Module not found**: Install package with `pip install -e .`
2. **Tests fail**: Ensure all dependencies are installed (`pip install -e ".[dev]"`)
3. **LSP errors about None**: Some type hints may show as errors but runtime works fine

## Dependencies

- python-dateutil
- pyyaml
- docopt
- pytest (dev)
