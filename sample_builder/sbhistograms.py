# IMPORT
import time
from sample_builder.sbbase import SBBase

from ROOT import TFile, gDirectory


# NOTE: speed up by get histogram name list at the beginning?

class SBHistograms(SBBase):

    def __init__(self, root_file_name, region_prefix, masses):
        super(SBHistograms, self).__init__(root_file_name, region_prefix, masses)

    def _get_histograms_mass(self, mass):
        name_dict = dict()
        process_list = list()
        name_list = list()
        self.logger.info("Getting list of region {} for Mx={} ...".format(self.region_prefix + self.masscut[str(mass)], mass))
        root_file = TFile(self.root_file_name)
        hash = gDirectory.GetListOfKeys()
        iter = hash.MakeIterator()
        key = iter.Next()
        self.logger.info(' -> Getting info from nominal histograms ...')
        start = time.time()
        while key:
            obj = key.ReadObj()
            name = obj.GetName()
            obj.Delete()
            key = iter.Next()
            if self.region_prefix + self.masscut[str(mass)] + "_" + self.disc in name:
                if self.signal_prefix in name and self.signal_prefix + str(mass) not in name: continue
                if self.signal_prefix + str(mass) + "Py8" in name: continue
                name_list.append(name)
        end = time.time()
        self.logger.info(" --> Spent {:.2f}s".format(end - start))
        root_file.cd("Systematics")
        hash = gDirectory.GetListOfKeys()
        iter = hash.MakeIterator()
        key = iter.Next()
        self.logger.info(' -> Getting info from variational histograms ...')
        start = time.time()
        while key:
            obj = key.ReadObj()
            name = obj.GetName()
            obj.Delete()
            key = iter.Next()
            if self.region_prefix + self.masscut[str(mass)] + "_" + self.disc in name:
                if self.signal_prefix in name and self.signal_prefix + str(mass) not in name: continue
                if self.signal_prefix + str(mass) + "Py8" in name: continue
                if "data" in name and self.disc + "_Sys" in name: continue
                if name.split('_Sys')[0] not in name_list: continue  # some inconsistency of nominal and systs
                name_list.append(name)
        end = time.time()
        self.logger.info(" --> Spent {:.2f}s".format(end - start))
        root_file.Close()
        for name in name_list:
            process_list.append(self._process(name))
        process_list = list(set(process_list))
        self.logger.debug(' -> process_list')
        self.logger.debug(process_list)
        for process in process_list:
            name_dict[process] = [h for h in name_list if process in h]
        self._data[str(mass)] = name_dict
        self.logger.debug(' -> name_dict')
        self.logger.debug(name_dict)

    def _process(self, name):
        return name.split('_')[0]

    def _get_data(self):
        for mass in self.masses:
            self._get_histograms_mass(mass)
