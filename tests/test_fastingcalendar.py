from datetime import date
from byzantine.fastingcalendar import FastingCalendar


class TestFastingCalendarGet:
    def test_fixed_date(self):
        fc = FastingCalendar("test_calendar.yml")
        results = fc.get(2024)
        dates = [d for d, v in results]

        assert date(2024, 1, 1) in dates
        assert date(2024, 6, 15) in dates

    def test_weekday_rules(self):
        fc = FastingCalendar("test_calendar.yml")
        results = fc.get(2024)
        results_dict = dict(results)

        wed_jan_10 = date(2024, 1, 10)
        assert wed_jan_10 in results_dict
        assert results_dict[wed_jan_10] == {"wed": "no_oil"}

        fri_jan_12 = date(2024, 1, 12)
        assert fri_jan_12 in results_dict
        assert results_dict[fri_jan_12] == {"fri": "no_oil"}

    def test_no_fast_period(self):
        fc = FastingCalendar("test_calendar.yml")
        results = fc.get(2024)
        results_dict = dict(results)

        mar_3 = date(2024, 3, 3)
        assert mar_3 in results_dict
        assert results_dict[mar_3] == {"sun": "no_fast"}


class TestFastingCalendarHtml:
    def test_html_output(self):
        fc = FastingCalendar("test_calendar.yml")
        html = fc.to_html(2024)

        assert "<table" in html
        assert "January" in html or "Januar" in html

    def test_html_with_lang(self):
        fc = FastingCalendar("test_calendar.yml")
        html = fc.to_html(2024, lang="en")

        assert "January" in html


class TestFastingCalendarMarkdown:
    def test_markdown_output(self):
        fc = FastingCalendar("test_calendar.yml")
        md = fc.to_markdown(2024)

        assert "|" in md
        assert "Start" in md
        assert "End" in md

    def test_markdown_title(self):
        fc = FastingCalendar("test_calendar.yml")
        md = fc.to_markdown(2024, lang="en")

        assert "# Fasting calendar" in md


class TestFastingCalendarOldStyle:
    def test_old_style_offset(self):
        fc = FastingCalendar("test_calendar.yml")
        results = fc.get(2024, old_style=True)
        dates = [d for d, v in results]

        jan_14 = date(2024, 1, 14)
        assert jan_14 in dates
