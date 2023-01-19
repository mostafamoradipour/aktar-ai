import logging
from logging.handlers import TimedRotatingFileHandler
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     datefmt='%m/%d/%y %H:%M:%S')
# from itertools import *  # cycle, count, ...
# from collections import deque  # and so on
# use tuples as more as possible
# TODO: Use Exception error handling
from service_db.db_api import Database
import time


logger = logging.getLogger(__name__)
# stream_h = logging.StreamHandler()
# file_h = logging.FileHandler('file.log')
# stream_h.setLevel(logging.WARNING)
# file_h.setLevel(logging.ERROR)
# formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# stream_h.setFormatter(formatter)
# file_h.setFormatter(formatter)
# logger.addHandler(stream_h)
# logger.addHandler(file_h)
handler = TimedRotatingFileHandler('timed_test.log', when='s', interval=5, backupCount=5)
logger.addHandler(handler)

for _ in range(6):
    logger.warning('This is a warning')
    logger.error('This is an error')
    time.sleep(5)
