import logging
import sys


def get_logger(filename):
    """ Define logger to write logs in specific file.
    mode='a' is appending if file already exists
    """
    logging.basicConfig(
        level=logging.INFO,
        encoding='utf-8',
        format="[{asctime}]:[{levelname}]:{message}",
        style='{',
        handlers=[
            logging.FileHandler(filename, mode='a'),
            logging.StreamHandler(sys.stdout),
        ]
    )
