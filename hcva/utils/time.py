from time import sleep


def call_sleep(logger=None, days=0, minutes=0, seconds=0):
    massage = f"Going to sleep for {minutes} minutes"
    if logger is not None:
        logger.info(massage)
    else:
        print(massage)
    sleep((days * 60 * 24) + (minutes * 60) + seconds)
