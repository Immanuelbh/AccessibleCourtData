from time import sleep, strftime, localtime


def curr_time(num_sep='-', date_time_sep='_'):
    return strftime(f"%d{num_sep}%m{num_sep}%Y{date_time_sep}%H{num_sep}%M{num_sep}%S", localtime())


def call_sleep(logger=None, days=0, hours=0, minutes=0, seconds=0):
    massage = f"Going to sleep for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    if logger is not None:
        logger.info(massage)
    else:
        print(massage)
    sleep((days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds)
