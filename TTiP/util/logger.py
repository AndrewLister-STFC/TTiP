"""
Centralised logging information to setup or fetch a logger.
"""
import logging
import sys

# Create the base logger so that other imports do not log.
logging.getLogger()


def setup_logger(name='ttip', debug=False, log_file='ttip.log'):
    """
    Setup a basic logger.

    Args:
        name (string, optional):
            The name of the logger to get. Defaults to "ttip".
        debug (bool, optional):
            Display debug output. Defaults to False
        log_file (string, optional):
            The file to log to. Defaults to "ttip.log".

    Returns:
        logger:
            The newly created logger.
    """
    FORMAT = '[%(asctime)s]  %(levelname)s %(filename)s: %(message)s'
    formatter = logging.Formatter(FORMAT, "%H:%M:%S")

    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    for h in logger.handlers:
        logger.removeHandler(h)

    logger.addHandler(handler)

    level = logging.INFO if not debug else logging.DEBUG
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    logger.addHandler(console)
    return get_logger(name)


def get_logger(name='ttip'):
    """
    Get the unique logger for the given name.
    This is a straight pass through but will be more intutive for people who
    have not used python logging.

    Args:
        name (string, optional):
            The name of the logger to get. Defaults to "ttip".

    Returns:
        logger: The logger for ttip.
    """
    return logging.getLogger(name)
