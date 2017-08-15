"""prelog stores log messages before logging is available.

A prelog instance has a compatible interface to a ``logging.Logger``.
You can use it whenever parts of your application already use logging
while the logging system is not yet setup, e.g. during config parsing.

The prelog logger stores all submitted messages and can pass them later
on to a real logger instance.
"""

import logging


class PreLogger(object):

    def __init__(self):
        self.msgs = []

    def debug(self, msg, *args, **kwargs):
        self.log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.log(logging.CRITICAL, msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self.msgs.append((level, msg, args, kwargs))

    def get_log_msgs(self):
        return self.msgs

    def get_num_msgs(self, level):
        num = 0
        for m in self.msgs:
            if m[0] == level:
                num += 1
        return num

    def to_logger(self, logger):
        for msg in self.msgs:
            logger.log(msg[0], msg[1], *msg[2], **msg[3])
