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
                    self._entries.append(("range", start, end, rules))
                else:
                    day = Day(date_spec)
                    self._entries.append(("fixed", day, value))

    def get(self, year: int | None = None) -> list:
        """Get all fasting days for a given year.

        Args:
            year: Year to calculate dates for. Defaults to current year.

        Returns:
            List of tuples: (date, name_or_rules)
        """
        from datetime import date

        if year is None:
            year = date.today().year

        result = []
        for entry in self._entries:
            if entry[0] == "fixed":
                _, day, value = entry
                result.append((day.get(year), value))
            else:
                _, start, end, rules = entry
                start_date = start.get(year)
                end_date = end.get(year)
                current = start_date
                while current <= end_date:
                    wd = current.weekday()
                    wd_name = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][wd]
                    if wd_name in rules:
                        result.append((current, {wd_name: rules[wd_name]}))
                    current = __import__("datetime").timedelta(days=1) + current
        return result
