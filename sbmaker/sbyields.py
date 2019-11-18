# IMPORT
from ROOT import TFile, TH1F, TDirectory, gDirectory, Double
from math import sqrt
from array import array
import copy


# Singleton: one ROOT file -> one instance (singleton not checked)

class SBYields():

    def __init__(self, root_file_name, region_prefix, binning, histograms, load, store):
        self._shape_systs = ['SysFATJET_Medium_JET_Comb_Baseline_Kin',
                             'SysFATJET_Medium_JET_Comb_TotalStat_Kin',
                             'SysFATJET_Medium_JET_Comb_Modelling_Kin',
                             'SysFATJET_Medium_JET_Comb_Tracking_Kin',
                             'SysFATJET_JER', 'SysFATJET_JMR',
                             'SysTAUS_TRUEHADDITAU_EFF_JETID_TOTAL',
                             'SysTAUS_TRUEHADDITAU_SME_TES_TOTAL',
                             'SysMET_SoftTrk_ResoPerp', 'SysMET_SoftTrk_ResoPara',
                             'SysMET_JetTrk_Scale', 'SysMET_SoftTrk_Scale', 
                             'SysPRW_DATASF', ]
        self._diboson = ['WWPw', 'WZPw', 'ZZPw']
        self._Wjets = ['Wbb', 'Wbc', 'Wbl', 'Wcc', 'Wcl', 'Wl']
        self._Zhf = ['Zbb', 'Zbc', 'Zbl', 'Zcc']
        self._Zlf = ['Zcl', 'Zl']
        self._Zee = ['ZeeSh221']
        self._top = ['ttbar', 'stop', 'stops', 'stopt', 'stopWt', 'ttbar_allhad', 'ttbar_nonallhad']
        self._for_histfitter = True
        self._do_merging = True
        self.binning = binning
        self._n_bins = len(self.binning) - 1
        self.root_file_name = root_file_name
        self.region_prefix = region_prefix
        self._disc = "effmHH"
        self._signal_prefix = "Hhhbbtautau"
        self.histograms = histograms if not load else self._load_histograms()
        self.load = load
        self.store = store
        self._yields = dict()
        self._get_yields()
        if self.store:
            self._save_yields()

    def _histogram_info(self, root_file, name):
        contents = [float(0.) for _ in range(self._n_bins)]
        errors = [float(0.) for _ in range(self._n_bins)]
        try:
            histogram = root_file.Get(name).Clone()
            histogram = histogram.Rebin(self._n_bins, name + "_rebinned", array('d', self.binning))
            assert self._n_bins == histogram.GetNbinsX()
            contents = [float("{0:.6f}".format(histogram.GetBinContent(c + 1))) for c in range(histogram.GetNbinsX())]
            errors = [float("{0:.6f}".format(histogram.GetBinError(c + 1))) for c in range(histogram.GetNbinsX())]
            del histogram
        except:
            pass  # TODO
        return contents, errors

    def _histogram_syst_info(self, root_file, syst_name, yields_process):
        noms = yields_process["nEvents"]
        try:
            histogram_up = root_file.Get("Systematics/" + syst_name + "__1up").Clone()
            histogram_up = histogram_up.Rebin(self._n_bins, "Systematics/" + syst_name + "__1up" + "_rebinned",
                                              array('d', self.binning))
            assert self._n_bins == histogram_up.GetNbinsX()
            ups = [float("{0:.6f}".format(histogram_up.GetBinContent(c + 1))) for c in range(histogram_up.GetNbinsX())]
            del histogram_up
        except:
            ups = noms
        try:
            histogram_do = root_file.Get("Systematics/" + syst_name + "__1down").Clone()
            histogram_do = histogram_do.Rebin(self._n_bins, "Systematics/" + syst_name + "__1down" + "_rebinned",
                                              array('d', self.binning))
            assert self._n_bins == histogram_do.GetNbinsX()
            downs = [float("{0:.6f}".format(histogram_do.GetBinContent(c + 1))) for c in
                     range(histogram_do.GetNbinsX())]
            del histogram_do
        except:
            downs = [float("{0:.6f}".format(2 * n - u)) for n, u in zip(noms, ups)]
        if sum(ups) < sum(downs):
            ups, downs = downs, ups
        return ups, downs

    def _systematic(self, name):
        return 'Sys' + name.split(self._disc + '_Sys')[1]

    def _pruning(self, yields_process, systematics_list, threshold):
        yields_process_updated = {}
        noms = yields_process["nEvents"]
        errors = yields_process["nEventsErr"]
        yields_process_updated["nEvents"] = noms
        yields_process_updated["nEventsErr"] = errors
        for systematic in systematics_list:
            ups = yields_process[systematic + "__1up"]
            downs = yields_process[systematic + "__1down"]
            if not self._do_merging:
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
                # TODO: negative -> ignore
            syst_var = [ups, downs]
            yields_process_updated[systematic.replace('Sys','ATLAS_')+'_hadhad'] = syst_var

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
        yields_mass_updated = {}
        yields_diboson = {}
        yields_Wjets = {}
        yields_Zhf = {}
        yields_Zlf = {}
        yields_Zee = {}
        yields_top = {}
        # HC
        keys = yields_mass['Zbb'].keys()
        self._init_yields_process(yields_diboson, keys)
        self._init_yields_process(yields_Wjets, keys)
        self._init_yields_process(yields_Zhf, keys)
        self._init_yields_process(yields_Zlf, keys)
        self._init_yields_process(yields_Zee, keys)
        self._init_yields_process(yields_top, keys)
        for process, yields_process in yields_mass.items():
            if process in self._diboson:
                self._sum_yields_process(yields_diboson, yields_process)
            elif process in self._Wjets:
                self._sum_yields_process(yields_Wjets, yields_process)
            elif process in self._Zhf:
                self._sum_yields_process(yields_Zhf, yields_process)
            elif process in self._Zlf:
                self._sum_yields_process(yields_Zlf, yields_process)
            elif process in self._Zee:
                self._sum_yields_process(yields_Zee, yields_process)
            elif process in self._top:
                self._sum_yields_process(yields_top, yields_process)
            else:
                yields_mass_updated[process] = yields_process
        yields_mass_updated['diboson'] = yields_diboson
        if not self._for_histfitter:
            yields_mass_updated['$W$+jets'] = yields_Wjets
            yields_mass_updated['$Z\\tau\\tau$+HF'] = yields_Zhf
            yields_mass_updated['$Z\\tau\\tau$+LF'] = yields_Zlf
            yields_mass_updated['$Zee$'] = yields_Zee
        else:
            yields_mass_updated['Wjets'] = yields_Wjets
            yields_mass_updated['Zhf'] = yields_Zhf
            yields_mass_updated['Zlf'] = yields_Zlf
            yields_mass_updated['Zee'] = yields_Zee
        yields_mass_updated['top'] = yields_top
        return yields_mass_updated

    def _pruning_after_merging(self, yields_mass, threshold):
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
                # TODO: negative -> ignore
            yields_mass_updated[process] = yields_process_tmp

        return yields_mass_updated

    def _get_yields(self):
        root_file = TFile(self.root_file_name)
        for mass, name_dict in self.histograms.items():
            yields_mass = {}
            total_bkg = 0
            for process, name_list in name_dict.items():
                for name in name_list:
                    if "Sys" not in name or process == 'data':
                        nEvents, _ = self._histogram_info(root_file, name)
                        if self._signal_prefix not in process and 'data' not in process:
                            total_bkg += sum(nEvents)
            print("mass {} bkg {}".format(mass, total_bkg))
            for process, name_list in name_dict.items():
                print("-> processing {} / {} ... ".format(mass, process))
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
                # TODO: is this correct? Not allowing negative yields?
                if sum(yields_process["nEvents"]) < 0:
                    continue
                if process != 'data':
                    yields_process = self._pruning(yields_process, systematics_list, 0.005)
                yields_mass[process] = yields_process
            if self._do_merging:
                yields_mass = self._merging(yields_mass)
                yields_mass = self._pruning_after_merging(yields_mass, 0.005)
            self._yields[mass] = yields_mass
        root_file.Close()

    @property
    def yields(self):
        return self._yields

    @staticmethod
    def _load_histograms():
        import pickle
        with open('/Users/bowen/PycharmProjects/SampleBuilderMaker/pickle_files/histograms.dictionary',
                  'rb') as histograms_pickle:
            return pickle.load(histograms_pickle)

    def _save_yields(self):
        import pickle
        with open('/Users/bowen/PycharmProjects/SampleBuilderMaker/pickle_files/yields.dictionary',
                  'wb') as yields_pickle:
            pickle.dump(self._yields, yields_pickle, 2)
