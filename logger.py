
# logger.py - Logging configuration and setup
#
# Copyright (C) 2026 Sergio Borghese <s.borghese@netresults.it>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

