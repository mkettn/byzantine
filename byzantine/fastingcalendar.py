NO_FAST = "no_fast"
NO_MEAT = "no_meat"
NO_DAIRY = "no_dairy"
NO_FISH = "no_fish"
NO_OIL = "no_oil"


class FastingCalendar:
    """Represents an Orthodox fasting calendar loaded from a YAML file.

    The YAML file format supports:
        - Fixed dates: "MMDD": "name"
        - Easter-relative: "e[+-]N[d|w]": "name"
        - Ranges with weekday rules: "MMDD..MMDD": { weekday: rule, ... }
    """

    def __init__(self, path: str):
        """Load calendar from a YAML file.

        Args:
            path: Path to the YAML configuration file.
        """
        import yaml
        from byzantine.day import Day

        with open(path) as f:
            data = yaml.safe_load(f)

        self._entries = []
        for entry in data:
            for date_spec, value in entry.items():
                if ".." in date_spec:
                    start_str, end_str = date_spec.split("..")
                    start = Day(start_str)
                    end = Day(end_str)
                    rules = value
                    is_easter_relative = start_str.startswith(
                        "e"
                    ) or end_str.startswith("e")
                    self._entries.append(
                        ("range", start, end, rules, is_easter_relative)
                    )
                else:
                    day = Day(date_spec)
                    is_easter_relative = date_spec.startswith("e")
                    self._entries.append(("fixed", day, value, is_easter_relative))

    def get(self, year: int | None = None, old_style: bool = False) -> list:
        """Get all fasting days for a given year.

        Args:
            year: Year to calculate dates for. Defaults to current year.
            old_style: If True, apply 13-day Julian calendar offset to fixed dates.

        Returns:
            List of tuples: (date, name_or_rules). Later rules override earlier ones.
        """
        from datetime import date, timedelta

        if year is None:
            year = date.today().year

        julian_offset = timedelta(days=13) if old_style else timedelta(days=0)

        calendar = {}
        for entry in self._entries:
            entry_type = entry[0]
            if entry_type == "fixed":
                _, day, value, is_easter = entry
                dt = day.get(year)
                if not is_easter and old_style:
                    dt += julian_offset
                if isinstance(value, dict) and "rule" in value:
                    calendar[dt] = value
                else:
                    calendar[dt] = value
            else:
                _, start, end, rules, is_easter = entry
                start_date = start.get(year)
                end_date = end.get(year)
                if not is_easter and old_style:
                    start_date += julian_offset
                    end_date += julian_offset
                current = start_date
                while current <= end_date:
                    wd = current.weekday()
                    wd_name = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][wd]
                    expanded_rules = self._expand_weekday_rules(rules)
                    if wd_name in expanded_rules:
                        rule_value = {wd_name: expanded_rules[wd_name]}
                        if current in calendar and isinstance(calendar[current], dict):
                            calendar[current].update(rule_value)
                        else:
                            calendar[current] = rule_value
                    current += timedelta(days=1)

        return [(dt, value) for dt, value in sorted(calendar.items())]

    def _expand_weekday_rules(self, rules: dict) -> dict:
        """Expand weekday range rules like 'mon..sun' to individual days."""
        if not isinstance(rules, dict):
            return rules
        ABBR2NUM = {
            "mon": 0,
            "tue": 1,
            "wed": 2,
            "thu": 3,
            "fri": 4,
            "sat": 5,
            "sun": 6,
        }
        expanded = {}
        for key, value in rules.items():
            if ".." in key:
                start_wd, end_wd = key.split("..")
                start_num = ABBR2NUM[start_wd.lower()]
                end_num = ABBR2NUM[end_wd.lower()]
                if start_num <= end_num:
                    for i in range(start_num, end_num + 1):
                        for wd_name, wd_num in ABBR2NUM.items():
                            if wd_num == i:
                                expanded[wd_name] = value
                                break
                else:
                    for i in range(start_num, 7):
                        for wd_name, wd_num in ABBR2NUM.items():
                            if wd_num == i:
                                expanded[wd_name] = value
                                break
                    for i in range(0, end_num + 1):
                        for wd_name, wd_num in ABBR2NUM.items():
                            if wd_num == i:
                                expanded[wd_name] = value
                                break
            elif "," in key:
                for wd in key.split(","):
                    expanded[wd.strip()] = value
            else:
                expanded[key] = value
        return expanded

    def to_html(
        self,
        year: int | None = None,
        old_style: bool = False,
        title: str = "",
        weekdays: list | None = None,
        months: list | None = None,
        inline_css: bool = True,
    ) -> str:
        """Generate HTML calendar output.

        Args:
            year: Year to generate calendar for. Defaults to current year.
            old_style: If True, use Julian calendar (13-day offset).
            title: Title for the calendar.
            weekdays: List of weekday abbreviations. Defaults to German [SO, MO, DI, ...].
            months: List of month names. Defaults to German [Januar, Februar, ...].
            inline_css: If True, embed CSS inline. If False, reference style.css.

        Returns:
            HTML string with monthly calendar tables.
        """
        from datetime import date, timedelta
        from calendar import monthrange
        import importlib.resources

        if year is None:
            year = date.today().year

        if weekdays is None:
            weekdays = ["SO", "MO", "DI", "MI", "DO", "FR", "SA"]
        if months is None:
            months = [
                "Januar",
                "Februar",
                "Marz",
                "April",
                "Mai",
                "Juni",
                "Juli",
                "August",
                "September",
                "Oktober",
                "November",
                "Dezember",
            ]

        fastdays = dict(self.get(year, old_style))

        html = f"<!DOCTYPE html><html><head><title>{title}</title>"

        if inline_css:
            css_content = (
                importlib.resources.files("byzantine.data")
                .joinpath("style.css")
                .read_text()
            )
            html += f"<style>{css_content}</style>"
        else:
            html += '<link rel="stylesheet" type="text/css" href="style.css"/></head>'
        html += f'<body><h1>{title}</h1><div class="grid">'

        for month in range(1, 13):
            first_day_of_month = date(year, month, 1)
            last_day_of_month = date(year, month, monthrange(year, month)[1])
            last_day_in_table = last_day_of_month + timedelta(
                days=6 - ((last_day_of_month.weekday() + 1) % 7)
            )
            curr_day = first_day_of_month

            if curr_day.weekday() != 6:
                curr_day = first_day_of_month - timedelta(
                    days=first_day_of_month.weekday() + 1
                )

            html += f"<div><table class='month'><tr><th colspan='7'>{months[month - 1]}</th></tr><tr class='wd'>"
            for wd in weekdays:
                html += f"<th>{wd}</th>"
            html += "</tr>"

            while curr_day <= last_day_in_table:
                if curr_day.weekday() == 6:
                    html += "<tr>"
                if (curr_day < first_day_of_month) or (curr_day > last_day_of_month):
                    html += '<td class="empty"></td>'
                else:
                    rule = fastdays.get(curr_day, {})
                    if isinstance(rule, dict) and "rule" in rule:
                        css_class = rule["rule"]
                    elif isinstance(rule, dict) and rule:
                        css_class = next(iter(rule.values()))
                    else:
                        css_class = "no_fast"
                    html += f'<td class="{css_class}">{curr_day.day}</td>'
                if curr_day.weekday() == 5:
                    html += "</tr>"
                curr_day += timedelta(days=1)

            html += "</table></div>"

        html += "</div></body></html>"
        return html
