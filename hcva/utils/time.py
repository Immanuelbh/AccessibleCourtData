from time import sleep


def call_sleep(logger=None, days=0, seconds=0):
    massage = f"Going to sleep for {days} day(s) and {seconds} second(s)"
    if logger is not None:
        logger.info(massage)
    else:
        print(massage)
    sleep((days * 60 * 60 * 24) + seconds)
