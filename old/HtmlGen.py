import logging
from FastingCalendar import FastingLevels, TD_ONE_DAY
from datetime import date, timedelta
from calendar import monthrange, day_abbr

_FL2HC = [ "f0", "f1", "f2", "f3", "f4", ]


def get_legend(transl):
    return '<div class="legend">' \
        + ''.join([f'<div><div class="lc {v}"></div><div>{transl[k+1]}</div></div>' for k,v in enumerate(_FL2HC[1:])]) \
        + '</div>'


def _write_month(year:int, month:int, fastdays:dict, transl, fd):
    first_day_of_month = date(year, month, 1)
    last_day_of_month = date(year, month, monthrange(year, month)[1])
    last_day_in_table = last_day_of_month+timedelta(days=6-((last_day_of_month.weekday()+1)%7))
    curr_day = first_day_of_month
    # move current day to last sunday
    if curr_day.weekday()!=6:
        curr_day = first_day_of_month-timedelta(days=first_day_of_month.weekday()+1)
    fd.write(f'<table class="month"><tr><th colspan="7">{transl["months"][first_day_of_month.month-1]}</th></tr><tr class="wd">')
    for d in transl["weekdays"]:
        fd.write(f'<th>{d}</th>')
    fd.write("</tr>")
    while curr_day <= last_day_in_table:
        if curr_day.weekday()==6: # start new row each sunday
            fd.write("<tr>")
        if (curr_day < first_day_of_month) or (curr_day > last_day_of_month):
            fd.write('<td class="empty"></td>')
        else:
            fd.write(f'<td class="{_FL2HC[fastdays.get(curr_day, FastingLevels.NO_FASTING).value]}">{curr_day.day}</td>')
        if curr_day.weekday()==5: # end row each saturday
            fd.write('</tr>')
        curr_day += TD_ONE_DAY
    fd.write('</table>')


def fastdays2html(year, fastdays, transl, htmlfile, title="", introduction="", footer=""):
    with open(htmlfile, 'w') as fd:
        fd.write(f'<!DOCTYPE html><html><head><title>{title}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>{introduction}<div class="grid">')
        for m in range(1,13):
            fd.write("<div>")
            _write_month(year, m, fastdays, transl, fd)
            fd.write("</div>")
        fd.write(f'</div>{footer}</body></html>')
