# IMPORT
import time
from array import array
from math import sqrt, log
from utils.logging_tools import get_logger

from ROOT import TFile


# Singleton: one ROOT file -> one instance (singleton not checked)

class SBSensitivities():
    """
    Calculate Z = sqrt(2*(s+b)log(1+s/b)-2*s) bin-by-bin
    """

    def __init__(self, root_file_name, region_prefix, binnings):
        self.binnings = binnings
        self.root_file_name = root_file_name
        self.region_prefix = region_prefix
        self._sensitivities = dict()
        self.logger = get_logger("SBS", "INFO")

    def _n_bins(self, binning):

        return len(binning) - 1

    def _significance(self, s, b):

        return sqrt(2. * (s + b) * log(1. + s / b) - 2. * s) if b != 0 else 0.

    def _histogram_info(self, root_file, name, binning):
        contents = [float(0.) for _ in range(self._n_bins(binning))]
        try:
            histogram = root_file.Get(name).Clone()
            histogram = histogram.Rebin(self._n_bins(binning), name + "_rebinned", array('d', binning))
            assert self._n_bins(binning) == histogram.GetNbinsX()
            contents = [float("{0:.6f}".format(histogram.GetBinContent(c + 1))) for c in range(histogram.GetNbinsX())]
            del histogram
        except:
            pass  # TODO

        return contents

    def _get_sensitivities(self, cache_name):
        root_file = TFile(self.root_file_name)
        for binstyle, binning in self.binnings.items():
            sensitivities_binning = {}
            histograms = self._load_histograms(cache_name)
            for mass, name_dict in histograms.items():
                n_bkg = [float(0.) for _ in range(self._n_bins(binning))]
                n_sig = [float(0.) for _ in range(self._n_bins(binning))]
                for process, name_list in name_dict.items():
                    for name in name_list:
                        if "Sys" in name or process == 'data':
                            continue
                        n_events = self._histogram_info(root_file, name, binning)
                        if self.signal_prefix not in process:
                            n_bkg = [b + n for b, n in zip(n_bkg, n_events)]
                        else:
                            n_sig = n_events
                sensitivities_mass = sqrt(sum([self._significance(s, b) ** 2 for s, b in zip(n_sig, n_bkg)]))
                self.logger.debug("Binning {} \tMass {} \tZ {}".format(binstyle, mass, sensitivities_mass))
                self.logger.debug('n_sig')
                self.logger.debug(n_sig)
                self.logger.debug('n_bkg')
                self.logger.debug(n_bkg)
                sensitivities_binning[mass] = sensitivities_mass

            self._sensitivities[binstyle] = sensitivities_binning

        root_file.Close()
        del root_file

    @property
    def sensitivities(self):
        return self._sensitivities

    def _load_histograms(self, cache_name):
        import pickle
        with open(cache_name, 'rb') as histograms_pickle:
            return pickle.load(histograms_pickle)

    def _save_sensitivities(self, pickle_file_name):
        import pickle
        with open(pickle_file_name, 'wb') as sensitivities_pickle:
            pickle.dump(self._sensitivities, sensitivities_pickle, 2)

    def save_sensitivities(self, cache_name, pickle_file_name):
        self._get_sensitivities(cache_name)
        self._save_sensitivities(pickle_file_name)
