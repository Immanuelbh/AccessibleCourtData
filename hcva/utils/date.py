import pandas as pd
from datetime import timedelta, date, datetime

SATURDAY = 6  # according to weekdays by datetime (monday=0, ...)


def get_day_before(d):
    prev = d - timedelta(1)
    if prev.weekday() == SATURDAY:
        prev = prev - timedelta(1)

    return prev


def get_yesterday():
    return get_day_before(datetime.today()).strftime('%d-%m-%Y')


def init_dates(date_start='1-1-1997', date_end=get_yesterday()):
    ds = date_start.split('-')
    es = date_end.split('-')
    s = date(int(ds[2]), int(ds[1]), int(ds[0]))
    e = date(int(es[2]), int(es[1]), int(es[0]))-timedelta(1)
    weekmask = "Sun Mon Tue Wed Thu Fri"
    dates = [d.strftime('%d-%m-%Y')
             for d in pd.bdate_range(start=s, end=e, freq='C', weekmask=weekmask)]
    return dates
