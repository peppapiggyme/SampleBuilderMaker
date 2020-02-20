# IMPORT
import copy, time
from array import array
from math import sqrt
from sample_builder.sbbase import SBBase

from ROOT import TFile


class SBYields(SBBase):

    def __init__(self, root_file_name, region_prefix, masses, binning):
        super(SBYields, self).__init__(root_file_name, region_prefix, masses)
        self.binning = binning
        self._n_bins = len(self.binning) - 1

    def _histogram_info(self, root_file, name):
        factor = 1.0
        if 'ZHtautau' in name:
            factor = 139 / (139 - 36.1)  # mc16d/e -> mc16a/d/e
            self.logger.info("  Scale ZHtautau mc16d/e -> mc16a/d/e, factor = {}".format(factor))
        contents = [float(0.) for _ in range(self._n_bins)]
        errors = [float(0.) for _ in range(self._n_bins)]
        try:
            histogram = root_file.Get(name).Clone()
            histogram = histogram.Rebin(self._n_bins, name + "_rebinned", array('d', self.binning))
            assert self._n_bins == histogram.GetNbinsX()
            contents = [factor * float("{0:.6f}".format(histogram.GetBinContent(c + 1))) for c in
                        range(histogram.GetNbinsX())]
            errors = [factor * float("{0:.6f}".format(histogram.GetBinError(c + 1))) for c in
                      range(histogram.GetNbinsX())]
            del histogram
        except:
            self.logger.warn("  Cannot get info from *HISTOGRAM* {} in *FILE* {}".format(name, root_file))
            self.logger.warn("   -> Will use default value: 0s")
        return contents, errors

    def _histogram_syst_info(self, root_file, syst_name, yields_process):
        factor = 1.0
        if 'ZHtautau' in syst_name:
            factor = 139 / (139 - 36.1)  # mc16d/e -> mc16a/d/e
            self.logger.info("  Scale ZHtautau mc16d/e -> mc16a/d/e, factor = {}".format(factor))
        noms = yields_process["nEvents"]
        try:
            histogram_up = root_file.Get("Systematics/" + syst_name + "__1up").Clone()
            histogram_up = histogram_up.Rebin(self._n_bins, "Systematics/" + syst_name + "__1up" + "_rebinned",
                                              array('d', self.binning))
            assert self._n_bins == histogram_up.GetNbinsX()
            ups = [factor * float("{0:.6f}".format(histogram_up.GetBinContent(c + 1))) for c in
                   range(histogram_up.GetNbinsX())]
            del histogram_up
        except:
            self.logger.debug(
                "  Up variation of {} does not exist, use default value: same as nominal".format(syst_name))
            ups = noms
        try:
            histogram_do = root_file.Get("Systematics/" + syst_name + "__1down").Clone()
            histogram_do = histogram_do.Rebin(self._n_bins, "Systematics/" + syst_name + "__1down" + "_rebinned",
                                              array('d', self.binning))
            assert self._n_bins == histogram_do.GetNbinsX()
            downs = [factor * float("{0:.6f}".format(histogram_do.GetBinContent(c + 1))) for c in
                     range(histogram_do.GetNbinsX())]
            del histogram_do
        except:
            self.logger.debug(
                "  Down variation of {} does not exist, use default value: symmetrise up variation".format(syst_name))
            downs = [float("{0:.6f}".format(2 * n - u)) for n, u in zip(noms, ups)]

        # if sum(ups) < sum(downs):
        #     ups, downs = downs, ups

        return ups, downs

    def _systematic(self, name):
        return 'Sys' + name.split(self.disc + '_Sys')[1]

    def _pruning(self, yields_process, systematics_list, threshold):
        """
        Renaming is here.
        If merge, only rename and put ups and downs in a list: [[ups], [downs]]
        """
        yields_process_updated = {}
        noms = yields_process["nEvents"]
        errors = yields_process["nEventsErr"]
        yields_process_updated["nEvents"] = noms
        yields_process_updated["nEventsErr"] = errors
        for systematic in systematics_list:
            ups = yields_process[systematic + "__1up"]
            downs = yields_process[systematic + "__1down"]
            if not self.do_merging:
                syst_up_diff_ratios = [(u - n) / n if n != 0. else float(0.) for n, u in zip(noms, ups)]
                syst_do_diff_ratios = [(n - d) / n if n != 0. else float(0.) for n, d in zip(noms, downs)]
                # Pruning
                n_up_sizable = sum(abs(u) > threshold for u in syst_up_diff_ratios)
                n_do_sizable = sum(abs(d) > threshold for d in syst_do_diff_ratios)
                n_ud_sizable = sum(abs(u + d) > 2 * threshold for u, d in zip(syst_up_diff_ratios, syst_do_diff_ratios))
                if n_up_sizable == 0 and n_do_sizable == 0:
                    continue
                if n_ud_sizable == 0:
                    continue
            syst_var = [ups, downs]
            import re
            yields_process_updated[re.sub('^%s' % 'Sys', 'ATLAS_', systematic) + '_hadhad'] = syst_var

        return yields_process_updated

    def _init_yields_process(self, my_yields_process, keys):
        for key in keys:
            if 'ATLAS' in key:
                my_yields_process[key] = [[0. for _ in range(self._n_bins)],
                                          [0. for _ in range(self._n_bins)]]
            else:
                my_yields_process[key] = [0. for _ in range(self._n_bins)]

    def _sum_yields_process(self, my_yields_process, yields_process):
        for key, values in yields_process.items():
            old_values = copy.deepcopy(my_yields_process[key])
            if 'ATLAS' in key:
                my_yields_process[key][0] = [o + v for o, v in zip(old_values[0], values[0])]
                my_yields_process[key][1] = [o + v for o, v in zip(old_values[1], values[1])]
            if 'nEventsErr' in key:
                my_yields_process[key] = [sqrt(o ** 2 + v ** 2) for o, v in zip(old_values, values)]
            if 'nEvents' in key:
                my_yields_process[key] = [o + v for o, v in zip(old_values, values)]
            del old_values

    def _merging(self, yields_mass):
        """
        TODO: improve this
        """
        yields_mass_updated = {}
        # yields_diboson = {}
        # yields_Wjets = {}
        yields_Zhf = {}
        yields_Zlf = {}
        # yields_Zee = {}
        # yields_top = {}
        yields_VH = {}
        yields_others = {}
        
        # HC
        keys = yields_mass['Zbb'].keys()

        # self._init_yields_process(yields_diboson, keys)
        # self._init_yields_process(yields_Wjets, keys)
        self._init_yields_process(yields_Zhf, keys)
        self._init_yields_process(yields_Zlf, keys)
        # self._init_yields_process(yields_Zee, keys)
        # self._init_yields_process(yields_top, keys)
        self._init_yields_process(yields_VH, keys)
        self._init_yields_process(yields_others, keys)
        
        for process, yields_process in yields_mass.items():
            # if process in self.diboson:
            #     self._sum_yields_process(yields_diboson, yields_process)
            # elif process in self.Wjets:
            #     self._sum_yields_process(yields_Wjets, yields_process)
            if process in self.Zhf:
                self._sum_yields_process(yields_Zhf, yields_process)
            elif process in self.Zlf:
                self._sum_yields_process(yields_Zlf, yields_process)
            # elif process in self.Zee:
            #     self._sum_yields_process(yields_Zee, yields_process)
            # elif process in self.top:
            #     self._sum_yields_process(yields_top, yields_process)
            elif process in self.VH:
                self._sum_yields_process(yields_VH, yields_process)
            elif process in self.others:
                self._sum_yields_process(yields_others, yields_process)
            else:
                yields_mass_updated[process] = yields_process

            

        # yields_mass_updated['diboson'] = yields_diboson
        # yields_mass_updated['Wjets'] = yields_Wjets
        yields_mass_updated['Zhf'] = yields_Zhf
        yields_mass_updated['Zlf'] = yields_Zlf
        # yields_mass_updated['Zee'] = yields_Zee
        # yields_mass_updated['top'] = yields_top
        yields_mass_updated['VH'] = yields_VH
        yields_mass_updated['others'] = yields_others

        return yields_mass_updated


    def _pruning_after_merging(self, yields_mass, threshold):
        """
        TODO: improve workflow
        workflow now: 1) rename, 2) merge bkgs, 3) pruning
        NOTE: the pruning can be skipped since the same treatment will be processed in HistFitter...
        """
        yields_mass_updated = {}
        for process, yields_process in yields_mass.items():
            noms = yields_process["nEvents"]
            if sum(n > 0 for n in noms) == 0: continue
            yields_process_tmp = copy.deepcopy(yields_process)
            for syst, updo in yields_process.items():
                if 'ATLAS' not in syst: continue
                ups = updo[0]
                downs = updo[1]
                syst_up_ratio = [u / n if n != 0. else float(1.) for u, n in zip(ups, noms)]
                syst_do_ratio = [d / n if n != 0. else float(1.) for d, n in zip(downs, noms)]
                syst_up_diff_ratios = [(u - n) / n if n != 0. else float(0.) for n, u in zip(noms, ups)]
                syst_do_diff_ratios = [(n - d) / n if n != 0. else float(0.) for n, d in zip(noms, downs)]
                # Pruning
                n_up_sizable = sum(abs(u) > threshold for u in syst_up_diff_ratios)
                n_do_sizable = sum(abs(d) > threshold for d in syst_do_diff_ratios)
                n_ud_sizable = sum(abs(u + d) > 2 * threshold for u, d in zip(syst_up_diff_ratios, syst_do_diff_ratios))
                if n_up_sizable == 0 and n_do_sizable == 0:
                    yields_process_tmp.pop(syst)
                    continue
                if n_ud_sizable == 0:
                    yields_process_tmp.pop(syst)
                    continue
                # to make fit stable, turn same-side into symmetric
                yields_process_tmp[syst][0] = [u if ur > 1. else 2 * n - d for u, d, n, ur in
                                               zip(ups, downs, noms, syst_up_ratio)]
                yields_process_tmp[syst][1] = [d if dr < 1. else 2 * n - u for u, d, n, dr in
                                               zip(ups, downs, noms, syst_do_ratio)]
            yields_mass_updated[process] = yields_process_tmp

        return yields_mass_updated

    def _get_data(self):
        root_file = TFile(self.root_file_name)
        from utils.pickle_io_tools import pickle_load
        histograms = pickle_load(self.cache_name)
        for mass, name_dict in histograms.items():
            yields_mass = {}
            total_bkg = 0
            for process, name_list in name_dict.items():
                if process in self.ignore: 
                    continue
                for name in name_list:
                    if "Sys" not in name or process == 'data':
                        nEvents, _ = self._histogram_info(root_file, name)
                        if self.signal_prefix not in process and 'data' not in process:
                            total_bkg += sum(nEvents)
            self.logger.info("mass {} bkg {:.2f}".format(mass, total_bkg))
            for process, name_list in name_dict.items():
                if process in self.ignore: 
                    continue
                self.logger.info(" -> processing {} / {} ... ".format(mass, process))
                yields_process = {}
                systematics_list = []
                for name in name_list:
                    if "Sys" not in name or process == 'data':
                        nEvents, nEventsErr = self._histogram_info(root_file, name)
                        yields_process.update({"nEvents": nEvents,
                                               "nEventsErr": nEventsErr})
                for name in name_list:
                    if 'Sys' in name:
                        syst_name = name.split('__')[0]
                        # fakes are data driven, should only include fakefactor-related systematics
                        if process == 'fakes' and 'SysFF_' not in syst_name:
                            continue
                        systematics_list.append(self._systematic(syst_name))
                        nEventsUp, nEventsDo = self._histogram_syst_info(root_file, syst_name, yields_process)
                        yields_process.update(
                            {self._systematic(syst_name) + "__1up": nEventsUp,
                             self._systematic(syst_name) + "__1down": nEventsDo})
                if sum(yields_process["nEvents"]) < 0:
                    continue
                if process != 'data':
                    yields_process = self._pruning(yields_process, systematics_list, 0.005)
                yields_mass[process] = yields_process
            if self.do_merging:
                yields_mass = self._merging(yields_mass)
                yields_mass = self._pruning_after_merging(yields_mass, 0.005)
            self._data[mass] = yields_mass
        root_file.Close()
