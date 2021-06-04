from time import sleep


def call_sleep(logger=None, days=0, hours=0, minutes=0, seconds=0):
    massage = f"Going to sleep for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    if logger is not None:
        logger.info(massage)
    else:
        print(massage)
    sleep((days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds)
