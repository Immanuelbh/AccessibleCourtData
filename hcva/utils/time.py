from time import sleep


def call_sleep(logger=None, minutes=0, seconds=0):
    massage = f"Going to sleep for {minutes} minutes"
    if logger is not None:
        logger.info(massage)
    else:
        print(massage)
    sleep((minutes * 60) + seconds)
