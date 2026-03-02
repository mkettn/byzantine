# byzantine

Orthodox fasting calendar library and CLI tool.

## Installation

```bash
pip install -e .
```

## Library Usage

```python
from byzantine import Day
from byzantine.fastingcalendar import FastingCalendar

# Parse dates
d = Day("0612")
print(d.get(2024))  # 2024-06-12

d = Day("e-7w<wed")
print(d.get(2024))  # Wednesday 7 weeks before Orthodox Easter

# Generate fasting calendar
fc = FastingCalendar("fastingcalendar.yml")
results = fc.get(2024)

# Generate HTML output
html = fc.to_html(year=2024, title="Fastenkalender 2024")
```

## CLI Usage

```bash
# Generate calendar for 2024
fasting-calendar fastingcalendar.yml -y 2024 -o calendar.html

# Old style (Julian calendar)
fasting-calendar fastingcalendar.yml -y 2026 --old-style -o calendar_old_style.html

# Custom title
fasting-calendar fastingcalendar.yml -y 2024 -t "My Calendar"
```

## YAML Format

The fasting calendar is defined in YAML with these formats:

- **Fixed dates**: `"MMDD": "name"`
- **Easter-relative**: `"e[+-]N[d|w]": "name"` (days/weeks relative to Orthodox Easter)
- **Ranges**: `"MMDD..MMDD": { weekday: rule, ... }`
- **Weekday rules**: Use `mon..fri`, `sat..sun`, `wed,fri` syntax

### Fasting Rules

- `no_fast` - Everything allowed
- `no_meat` - No meat, dairy, eggs, fish
- `no_dairy` - No dairy, eggs, fish
- `no_fish` - No fish
- `no_oil` - No oil

## Date String Format

The `Day` class supports:

- `"MMDD"` - Fixed solar date (e.g., `"0612"` = June 12)
- `"e[+-]N[d|w]"` - Days/weeks relative to Orthodox Easter (e.g., `"e+50d"`, `"e-3w"`)
- `"e[+-]N[d|w][>|>]weekday"` - Adjust to next/previous weekday (e.g., `"e-7w<wed"`)

Weekdays: mon, tue, wed, thu, fri, sat, sun
