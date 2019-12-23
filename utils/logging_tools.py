import logging


def get_logger(name, msglvl):
    """
    set up a standard python Logger
    :param name: string
    :param msglvl: string choose from DEBUG, INFO, WARNING, ERROR
    :return: Logger()
    """
    level = {"DEBUG": logging.DEBUG,
             "INFO": logging.INFO,
             "WARNING": logging.WARNING,
             "ERROR": logging.ERROR}
    logging.basicConfig(level=level[msglvl], format='%(asctime)s %(levelname)s:\t%(message)s')
    logger = logging.getLogger(name)

    return logger
