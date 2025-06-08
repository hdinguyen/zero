import logging
from colorlog import ColoredFormatter

LOG_COLORS = {
    'DEBUG':    'cyan',
    'INFO':     'green', 
    'WARNING':  'yellow',
    'ERROR':    'red',
    'CRITICAL': 'red,bg_white',
}

SECONDARY_LOG_COLORS = {
    'message': {
        'DEBUG':    'white',
        'INFO':     'white',
        'WARNING':  'white',
        'ERROR':    'white',
        'CRITICAL': 'white',
    }
}

LOG_LEVEL = logging.DEBUG
LOGFORMAT = "%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"

formatter = ColoredFormatter(
    LOGFORMAT,
    log_colors=LOG_COLORS,
    secondary_log_colors=SECONDARY_LOG_COLORS,
    style='%'
)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)

logger = logging.getLogger('globalLogger')
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)
logger.propagate = False