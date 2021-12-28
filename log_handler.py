from datetime import datetime
from enum import Enum


class LOG_LEVEL(Enum):
    DEBUG = 0
    INFO = 1
    NOTICE = 2
    ERROR = 3
    CRITICAL = 4


CURRENT_LOG_FILE = 'execution_log.txt'
CURRENT_LOG_LEVEL = LOG_LEVEL.NOTICE.value


def set_log_file(filename):
    """Changes the name of the file where the log is written. This is used
    e.g. if the logs for a specific connection should be written in its own
    file.

    Args:
        filename (String): The path to the log file
    """
    global CURRENT_LOG_FILE

    if filename:
        CURRENT_LOG_FILE = filename
    else:
        CURRENT_LOG_FILE = 'execution_log.txt'


def get_log_file():
    global CURRENT_LOG_FILE
    return CURRENT_LOG_FILE


def set_log_level(level):
    """Changes the log level used to determine, which events should be logged.

    Args:
        level (LOG_LEVEL): The minimum severity of events to be written in logs
    """
    global CURRENT_LOG_LEVEL

    if level:
        CURRENT_LOG_LEVEL = level.value
    else:
        CURRENT_LOG_LEVEL = LOG_LEVEL.NOTICE.value


def get_log_level():
    global CURRENT_LOG_LEVEL
    return CURRENT_LOG_LEVEL


def write_log(level, message):
    """
    Writes a log entry in the system log

    Args:
        level (LOG_LEVEL): [description]
        message (String): [description]
    """

    # If run manually, all this may be of interest to the user
    print(message)

    if level.value >= get_log_level():
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        lfile = open(get_log_file(), 'a')
        lfile.writelines("\n{}: {:<8} {}".format(now, level.name, message))
        lfile.close()
