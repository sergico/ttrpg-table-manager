# udp_ping_tool/logger.py
import logging
from datetime import datetime
import pytz


def setup_logging(log_file="ttrp.table.mng.log", verbose=False):
    logger = logging.getLogger("udp_ping")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s %(tz)s] [%(threadName)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    class TimezoneFilter(logging.Filter):
        def filter(self, record):
            local_dt = datetime.now(pytz.timezone('UTC')).astimezone()
            record.tz = local_dt.strftime('%z')
            return True

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(TimezoneFilter())
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(TimezoneFilter())
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger

g_logger = setup_logging(log_file='ttrpg.table.logger.log', verbose=True)

