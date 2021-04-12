import logging as s_logging
import sys

class CustomFormatter(s_logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[92m"
    reset = "\x1b[0m"
    format = (
        "%(asctime)s - %(message)s"
        # "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        s_logging.DEBUG: grey + format + reset,
        s_logging.INFO: yellow + format + reset,
        s_logging.WARNING: green + format + reset,
        s_logging.ERROR: red + format + reset,
        s_logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = s_logging.Formatter(log_fmt)
        return formatter.format(record)

def init_logging(filename: str) -> s_logging.Logger:

    logging = s_logging.getLogger(filename)
    logging.setLevel(s_logging.DEBUG)
    ch = s_logging.StreamHandler(sys.stdout)
    ch.setLevel(s_logging.DEBUG)

    ch.setFormatter(CustomFormatter())
    logging.addHandler(ch)
    return logging
