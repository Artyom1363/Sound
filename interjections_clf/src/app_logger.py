import logging
import argparse

_log_format = '%(asctime)s\t%(name)s\t%(levelname)s\t>\t%(message)s'
LOG_FILE_PATH = '/var/log/cutting.log'


def get_file_handler(filepath=None):
    file_handler = None
    if filepath is not None:
        file_handler = logging.FileHandler(filepath)
    else:
        file_handler = logging.FileHandler(LOG_FILE_PATH)

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler(level=None):
    stream_handler = logging.StreamHandler()

    if level is not None:
        stream_handler.setLevel(level)
    else:
        stream_handler.setLevel(logging.DEBUG)

    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    if len(logger.handlers) > 0:
        return logger

    parser = argparse.ArgumentParser()
    parser.add_argument('--prod', action='store_true', help='Set if running on production')

    args = parser.parse_args()
    logger.addHandler(get_stream_handler())

    if args.prod:
        logger.setLevel('INFO')
        logger.addHandler(get_file_handler())
    else:
        logger.setLevel('DEBUG')

    return logger