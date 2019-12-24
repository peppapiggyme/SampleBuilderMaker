# IMPORT
import time
from array import array
from math import sqrt, log
from sample_builder.sbbase import SBBase

from ROOT import TFile


# Singleton: one ROOT file -> one instance (singleton not checked)

class SBSensitivities(SBBase):
    """
    Calculate Z = sqrt(2*(s+b)log(1+s/b)-2*s) bin-by-bin
    """

    def __init__(self, root_file_name, region_prefix, masses, binnings):
        super().__init__(root_file_name, region_prefix, masses)
        self.binnings = binnings

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
            self.logger.warn(" Cannot get *HISTOGRAM* {} from *FILE* {}".format(root_file, name))
            self.logger.warn("  -> Will use default values: 0s")

        return contents

    def _get_data(self):
        root_file = TFile(self.root_file_name)
        for binstyle, binning in self.binnings.items():
            sensitivities_binning = {}
            from utils.pickle_io_tools import pickle_load
            histograms = pickle_load(self.cache_name)
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
                self.logger.debug(" Binning {} \tMass {} \tZ {}".format(binstyle, mass, sensitivities_mass))
                self.logger.debug('  *n_sig*')
                self.logger.debug(n_sig)
                self.logger.debug('  *n_bkg*')
                self.logger.debug(n_bkg)
                sensitivities_binning[mass] = sensitivities_mass

            self._data[binstyle] = sensitivities_binning

        root_file.Close()
