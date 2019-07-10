import logging

def get_logger(name):
    return logging.getLogger(name)

def init_logging(level=logging.DEBUG):
    logging.basicConfig(level=level,
        format='[%(name)s:%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s')

init_logging()