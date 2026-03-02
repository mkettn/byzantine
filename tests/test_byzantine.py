from datetime import date
from byzantine import Day


class TestDaySolar:
    def test_simple_date(self):
        d = Day("0612")
        assert d.get(2024) == date(2024, 6, 12)

    def test_jan_1st(self):
        d = Day("0101")
        assert d.get(2024) == date(2024, 1, 1)

    def test_dec_31st(self):
        d = Day("1231")
        assert d.get(2024) == date(2024, 12, 31)

    def test_leap_year_date(self):
        d = Day("0229")
        assert d.get(2024) == date(2024, 2, 29)

    def test_different_year(self):
        d = Day("0612")
        assert d.get(2023) == date(2023, 6, 12)


class TestDayEasterRelative:
    def test_e_plus_days(self):
        d = Day("e+50d")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024 + __import__("datetime").timedelta(days=50)

    def test_e_minus_days(self):
        d = Day("e-50d")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024 - __import__("datetime").timedelta(days=50)

    def test_e_plus_weeks(self):
        d = Day("e+7w")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024 + __import__("datetime").timedelta(days=49)

    def test_e_minus_weeks(self):
        d = Day("e-3w")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024 - __import__("datetime").timedelta(days=21)


class TestDayWeekday:
    def test_succ_weekday(self):
        d = Day("e+0d>sun")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == date(2024, 5, 5)
        assert d.get(2024).weekday() == 6

    def test_prev_weekday(self):
        d = Day("e-7w<wed")
        easter_2024 = date(2024, 5, 5)
        expected = easter_2024 - __import__("datetime").timedelta(days=49)
        while expected.weekday() != 2:
            expected -= __import__("datetime").timedelta(days=1)
        assert d.get(2024).weekday() == 2

    def test_plus_50d_after_easter_sunday(self):
        d = Day("e+50d>sun")
        easter_2024 = date(2024, 5, 5)
        base = easter_2024 + __import__("datetime").timedelta(days=50)
        while base.weekday() != 6:
            base += __import__("datetime").timedelta(days=1)
        assert d.get(2024) == base


class TestDayDefaultYear:
    def test_default_year_is_current(self):
        d = Day("0101")
        today = date.today()
        result = d.get()
        assert result.month == 1
        assert result.day == 1


class TestDayStr:
    def test_str_representation(self):
        d = Day("0612")
        assert str(d) == 'Day("0612")'

    def test_str_easter(self):
        d = Day("e+50d")
        assert str(d) == 'Day("e+50d")'
