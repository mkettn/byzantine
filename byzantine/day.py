from datetime import timedelta, date
from dateutil.easter import easter, EASTER_ORTHODOX


class Day:
    """Represents a calendar day, either a fixed solar date or relative to Orthodox Easter.

    Date strings:
        - "MMDD" : Fixed solar date (e.g., "0612" = June 12, "1225" = December 25)
        - "e[+-]N[d|w]" : Days/weeks relative to Orthodox Easter (e.g., "e+50d", "e-3w")
        - "e[+-]N[d|w][>|>]weekday" : As above, then adjust to next/previous weekday

    Weekdays: mon, tue, wed, thu, fri, sat, sun

    Examples:
        >>> Day("0612").get(2024)
        datetime.date(2024, 6, 12)

        >>> Day("e+50d").get(2024)  # 50 days after Orthodox Easter 2024
        datetime.date(2024, 6, 24)

        >>> Day("e-7w<wed").get(2024)  # Wednesday 7 weeks before Orthodox Easter
        datetime.date(2024, 3, 20)
    """

    def _lunar(self, dstr: str):
        """Parse Easter-relative date string (starts with 'e')."""
        d = 0
        nbuf = ""
        for i, c in enumerate(dstr[1:]):  # first char is e
            i += 1
            if c.isnumeric() or c in "+-":
                nbuf += c
                continue
            if c in "wd":
                d = int(nbuf) * (7 if c == "w" else 1)
                nbuf = ""  # clear n
                continue
            if c in "<>":
                ABBR2NUM = {
                    "mon": 0,
                    "tue": 1,
                    "wed": 2,
                    "thu": 3,
                    "fri": 4,
                    "sat": 5,
                    "sun": 6,
                }
                wd = dstr[i + 1 : i + 4].lower()
                if c == "<":
                    self._prevwd = ABBR2NUM[wd]
                else:
                    self._succwd = ABBR2NUM[wd]
                break
        if len(nbuf) > 0:  # days in nbuf assumend
            d = int(nbuf)
        self._delta = timedelta(days=d)

    def _solar(self, d: str):
        """Parse fixed solar date string (MMDD format)."""
        self._month = int(d[0:2])
        self._day = int(d[2:4])
        assert self._month > 0 and self._month <= 12
        assert self._day > 0 and self._day <= 31

    def __init__(self, d: str):
        """Initialize with a date string.

        Args:
            d: Date string in one of the supported formats.
        """
        self._succwd = None
        self._prevwd = None
        self._date = d
        self._pascha = d[0] == "e"
        if self._pascha:
            self._lunar(d)
        else:
            self._solar(d)

    def get(self, year: int | None = None):
        """Get the date for a given year.

        Args:
            year: Year to calculate the date for. Defaults to current year.

        Returns:
            A datetime.date object representing the parsed date.
        """
        if year is None:
            year = date.today().year
        ret = None
        if self._pascha:
            ret = easter(year, EASTER_ORTHODOX)
            ret += self._delta
            retwd = ret.weekday()
            # logic for "mon/tue/... before/after"
            one_day = timedelta(days=1)
            if self._succwd != None:
                while ret.weekday() != self._succwd:
                    ret += one_day
            elif self._prevwd != None:
                while ret.weekday() != self._prevwd:
                    ret -= one_day
            # else nothing changes
        else:
            ret = date(year, self._month, self._day)
        return ret

    def is_easter_relative(self) -> bool:
        """Check if this date is relative to Orthodox Easter.

        Returns:
            True if the date string starts with 'e', False otherwise.
        """
        return self._pascha

    def __str__(self):
        return f'{__class__.__name__}("{self._date}")'
