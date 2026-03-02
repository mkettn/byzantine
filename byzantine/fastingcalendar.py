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
            List of tuples: (date, name_or_rules)
        """
        from datetime import date, timedelta

        if year is None:
            year = date.today().year

        julian_offset = timedelta(days=13) if old_style else timedelta(days=0)

        result = []
        for entry in self._entries:
            entry_type = entry[0]
            if entry_type == "fixed":
                _, day, value, is_easter = entry
                dt = day.get(year)
                if not is_easter and old_style:
                    dt += julian_offset
                result.append((dt, value))
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
                        result.append((current, {wd_name: expanded_rules[wd_name]}))
                    current += timedelta(days=1)
        return result

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
