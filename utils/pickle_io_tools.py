import pickle
from utils.logging_tools import get_logger

pickle_logger = get_logger("Pickle", "INFO")


def pickle_save(data, pickle_file_name):
    with open(pickle_file_name, 'wb') as pickle_file:
        pickle.dump(data, pickle_file)
    pickle_logger.info("Pickle file {} saved".format(pickle_file_name))


def pickle_load(pickle_file_name):
    pickle_file = open(pickle_file_name, 'rb')
    pickle_logger.info("Pickle file {} loaded".format(pickle_file_name))
    return pickle.load(pickle_file)
