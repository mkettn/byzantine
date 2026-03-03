from datetime import date, timedelta
from byzantine import Day
import pytest


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

    def test_all_months_first_day(self):
        """Test first day of each month"""
        for month in range(1, 13):
            month_str = f"{month:02d}01"
            d = Day(month_str)
            result = d.get(2024)
            assert result.month == month
            assert result.day == 1

    def test_all_months_last_day(self):
        """Test last day of each month"""
        last_days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for month, last_day in enumerate(last_days, 1):
            day_str = f"{month:02d}{last_day:02d}"
            d = Day(day_str)
            result = d.get(2024)
            assert result.month == month
            assert result.day == last_day

    def test_multiple_years_same_day(self):
        """Test same day across multiple years"""
        d = Day("0215")
        for year in [2020, 2023, 2024, 2025, 2030]:
            result = d.get(year)
            assert result.month == 2
            assert result.day == 15
            assert result.year == year


class TestDayEasterRelative:
    def test_e_plus_days(self):
        d = Day("e+50d")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024 + timedelta(days=50)

    def test_e_minus_days(self):
        d = Day("e-50d")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024 - timedelta(days=50)

    def test_e_plus_weeks(self):
        d = Day("e+7w")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024 + timedelta(days=49)

    def test_e_minus_weeks(self):
        d = Day("e-3w")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024 - timedelta(days=21)

    def test_e_zero_days(self):
        """Test Easter itself (e+0d)"""
        d = Day("e+0d")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024

    def test_e_zero_weeks(self):
        """Test Easter itself (e+0w)"""
        d = Day("e+0w")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024

    def test_e_large_positive_offset(self):
        """Test large positive offset"""
        d = Day("e+365d")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == easter_2024 + timedelta(days=365)

    def test_e_large_negative_offset(self):
        """Test large negative offset (crosses year boundary)"""
        d = Day("e-100d")
        easter_2024 = date(2024, 5, 5)
        result = d.get(2024)
        assert result == easter_2024 - timedelta(days=100)
        assert result.year == 2024  # Should still be in 2024 (Feb 2)

    def test_e_different_years(self):
        """Test Easter dates across different years"""
        # Easter dates vary each year
        d_2023 = Day("e+0d")
        d_2024 = Day("e+0d")
        d_2025 = Day("e+0d")

        easter_2023 = d_2023.get(2023)
        easter_2024 = d_2024.get(2024)
        easter_2025 = d_2025.get(2025)

        # Easter dates should be different
        assert easter_2023 != easter_2024
        assert easter_2024 != easter_2025


class TestDayWeekday:
    def test_succ_weekday(self):
        d = Day("e+0d>sun")
        easter_2024 = date(2024, 5, 5)
        assert d.get(2024) == date(2024, 5, 5)
        assert d.get(2024).weekday() == 6

    def test_prev_weekday(self):
        d = Day("e-7w<wed")
        easter_2024 = date(2024, 5, 5)
        expected = easter_2024 - timedelta(days=49)
        while expected.weekday() != 2:
            expected -= timedelta(days=1)
        assert d.get(2024).weekday() == 2

    def test_plus_50d_after_easter_sunday(self):
        d = Day("e+50d>sun")
        easter_2024 = date(2024, 5, 5)
        base = easter_2024 + timedelta(days=50)
        while base.weekday() != 6:
            base += timedelta(days=1)
        assert d.get(2024) == base

    def test_all_weekdays_forward(self):
        """Test finding next occurrence of each weekday"""
        weekdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for i, wd in enumerate(weekdays):
            d = Day(f"e+0d>{wd}")
            result = d.get(2024)
            assert result.weekday() == i

    def test_all_weekdays_backward(self):
        """Test finding previous occurrence of each weekday"""
        weekdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for i, wd in enumerate(weekdays):
            d = Day(f"e+0d<{wd}")
            result = d.get(2024)
            assert result.weekday() == i

    def test_weekday_same_day(self):
        """If date is already the target weekday, should return same date"""
        # May 5, 2024 is Easter (Sunday)
        d = Day("e+0d>sun")
        result = d.get(2024)
        assert result == date(2024, 5, 5)
        assert result.weekday() == 6  # Sunday

    def test_weekday_with_offset(self):
        """Test weekday adjustment after offset"""
        d = Day("e-7w>mon")
        result = d.get(2024)
        assert result.weekday() == 0  # Monday

    def test_complex_offset_and_weekday(self):
        """Test combining large offsets with weekday selection"""
        d = Day("e+100d<fri")
        result = d.get(2024)
        assert result.weekday() == 4  # Friday


class TestDayDefaultYear:
    def test_default_year_is_current(self):
        d = Day("0101")
        today = date.today()
        result = d.get()
        assert result.month == 1
        assert result.day == 1
        assert result.year == today.year

    def test_default_year_easter_relative(self):
        """Default year should work for Easter-relative dates too"""
        d = Day("e+0d")
        result = d.get()
        today = date.today()
        assert result.year == today.year


class TestDayStr:
    def test_str_representation(self):
        d = Day("0612")
        assert str(d) == 'Day("0612")'

    def test_str_easter(self):
        d = Day("e+50d")
        assert str(d) == 'Day("e+50d")'

    def test_str_with_weekday_forward(self):
        d = Day("e+0d>sun")
        assert str(d) == 'Day("e+0d>sun")'

    def test_str_with_weekday_backward(self):
        d = Day("e-7w<wed")
        assert str(d) == 'Day("e-7w<wed")'


class TestDayIsEasterRelative:
    def test_solar_date_not_easter_relative(self):
        d = Day("0612")
        assert d.is_easter_relative() is False

    def test_easter_date_is_relative(self):
        d = Day("e+0d")
        assert d.is_easter_relative() is True

    def test_easter_with_offset_is_relative(self):
        d = Day("e-50d")
        assert d.is_easter_relative() is True

    def test_easter_with_weekday_is_relative(self):
        d = Day("e+0d>sun")
        assert d.is_easter_relative() is True


class TestDayEdgeCases:
    def test_mid_range_dates(self):
        """Test dates in the middle of the year"""
        d = Day("0701")
        assert d.get(2024) == date(2024, 7, 1)

    def test_consecutive_dates(self):
        """Test consecutive dates work correctly"""
        d1 = Day("0101")
        d2 = Day("0102")
        assert d2.get(2024) == d1.get(2024) + timedelta(days=1)

    def test_same_instance_multiple_years(self):
        """Same Day instance should work for multiple years"""
        d = Day("0615")
        for year in range(2000, 2050):
            result = d.get(year)
            assert result.year == year
            assert result.month == 6
            assert result.day == 15
