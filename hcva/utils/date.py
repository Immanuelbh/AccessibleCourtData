from datetime import timedelta, date, datetime
import pandas as pd
from dateutil.parser import parse

SATURDAY = 6  # according to weekdays by datetime (monday=0, ...)


def get_day_before(date_):
    prev = date_ - timedelta(1)
    if prev.weekday() == SATURDAY:
        prev = prev - timedelta(1)

    return prev


def get_yesterday():
    return get_day_before(datetime.today()).strftime('%d-%m-%Y')


def init_dates(date_start='1-1-1997', date_end=get_yesterday()):
    return get_dates_range(date_start, date_end)


def get_dates_range(date_start, date_end):
    ds = date_start.split('-')
    de = date_end.split('-')
    s = date(int(ds[2]), int(ds[1]), int(ds[0]))
    e = date(int(de[2]), int(de[1]), int(de[0]))
    weekmask = "Sun Mon Tue Wed Thu Fri"
    dates = [d.strftime('%d-%m-%Y')
             for d in pd.bdate_range(start=s, end=e, freq='C', weekmask=weekmask)]
    return dates


def create_gap_dates(latest_db_date, yesterday):
    return get_dates_range(latest_db_date, yesterday)


def get_gap_dates(latest_db_date):
    dates = []
    yesterday = get_yesterday()
    date1 = parse(latest_db_date)
    date2 = parse(yesterday)
    if date1 < date2:
        dates = create_gap_dates(latest_db_date, yesterday)
    return dates
