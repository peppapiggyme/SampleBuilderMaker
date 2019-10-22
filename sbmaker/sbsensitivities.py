# IMPORT
from ROOT import TFile, TH1F, TDirectory, gDirectory, Double
from math import sqrt, log
from array import array
import copy


# Singleton: one ROOT file -> one instance (singleton not checked)

class SBSensitivities():
    """
    Calculate Z = sqrt(2*(s+b)log(1+s/b)-2*s) bin-by-bin
    """

    def __init__(self, root_file_name, region_prefix, binnings, histograms, load, store):
        self.binnings = binnings
        self.root_file_name = root_file_name
        self.region_prefix = region_prefix
        self._disc = "subsmhh"
        self._signal_prefix = "Hhhbbtautau"
        self.histograms = histograms if not load else self._load_histograms()
        self.load = load
        self.store = store
        self._sensitivities = dict()
        self._get_sensitivities()
        if self.store:
            self._save_sensitivities()

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

    def _get_sensitivities(self):
        root_file = TFile(self.root_file_name)
        for binstyle, binning in self.binnings.items():
            sensitivities_binning = {}
            for mass, name_dict in self.histograms.items():
                n_bkg = [float(0.) for _ in range(self._n_bins(binning))]
                n_sig = [float(0.) for _ in range(self._n_bins(binning))]
                for process, name_list in name_dict.items():
                    for name in name_list:
                        if "Sys" in name or process == 'data':
                            continue
                        n_events = self._histogram_info(root_file, name, binning)
                        if self._signal_prefix not in process:
                            n_bkg = [b + n for b, n in zip(n_bkg, n_events)]
                        else:
                            n_sig = n_events
                sensitivities_mass = sqrt(sum([self._significance(s, b) ** 2 for s, b in zip(n_sig, n_bkg)]))
                # print("Binning {} \tMass {} \tZ {}".format(binstyle, mass, sensitivities_mass))
                # print(n_sig, n_bkg)
                sensitivities_binning[mass] = sensitivities_mass
            # print("")
            self._sensitivities[binstyle] = sensitivities_binning

        root_file.Close()
        del root_file

    @property
    def sensitivities(self):
        return self._sensitivities

    @staticmethod
    def _load_histograms():
        import pickle
        with open('/Users/bowen/PycharmProjects/SampleBuilderMaker/pickle_files/histograms.dictionary',
                  'rb') as histograms_pickle:
            return pickle.load(histograms_pickle)

    def _save_sensitivities(self):
        import pickle
        with open('/Users/bowen/PycharmProjects/SampleBuilderMaker/pickle_files/sensitivities.dictionary',
                  'wb') as sensitivities_pickle:
            pickle.dump(self._sensitivities, sensitivities_pickle, 2)
