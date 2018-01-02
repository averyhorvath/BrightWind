"""
Configuration for the logger
"""

from __future__ import absolute_import
import sys
import logging
from datetime import datetime

LOG = logging.getLogger()

LOG.setLevel('INFO')

log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(threadName)s]  %(message)s")

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)

LOG.addHandler(console_handler)

filepath = './log/merra-two-' + datetime.now().strftime('%Y-%m-%d') + ".log"
file_handler = logging.FileHandler(filepath)
file_handler.setFormatter(log_formatter)
LOG.addHandler(file_handler)


def log_system_error(exception_type, exception_value, exception_traceback):
    LOG.error('', exc_info=(exception_type, exception_value, exception_traceback))


sys.excepthook = log_system_error
