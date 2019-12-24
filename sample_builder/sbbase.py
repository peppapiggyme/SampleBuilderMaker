# IMPORT
import time
from utils.logging_tools import get_logger
from utils.pickle_io_tools import pickle_save, pickle_load


# Singleton: one ROOT file -> one instance (singleton not checked)

class SBBase(object):

    def __init__(self, root_file_name, region_prefix, masses):
        self.root_file_name = root_file_name
        self.region_prefix = region_prefix
        self.masses = masses
        self._data = dict()
        self.logger = get_logger("SB", "INFO")

    def _get_data(self):
        pass

    @property
    def data(self):
        return self._data

    def _save_data(self, pic_name):
        pickle_save(self._data, pic_name)

    def save_data(self, pic_name):
        self._get_data()
        self._save_data(pic_name)
