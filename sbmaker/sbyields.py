# IMPORT
from ROOT import TFile, TH1F, TDirectory, gDirectory, Double
from math import sqrt
import copy


# Singleton: one ROOT file -> one instance (singleton not checked)

class SBYields():

    def __init__(self, root_file_name, region_prefix, histograms, load, store):
        self._shape_systs = ['SysFATJET_Medium_JET_Comb_Baseline_Kin',
                             'SysFATJET_Medium_JET_Comb_TotalStat_Kin',
                             'SysFATJET_Medium_JET_Comb_Modelling_Kin',
                             'SysFATJET_Medium_JET_Comb_Tracking_Kin',
                             'SysFATJET_JER', 'SysFATJET_JMR',
                             'SysTAUS_TRUEHADDITAU_EFF_JETID_TOTAL',
                             'SysTAUS_TRUEHADDITAU_SME_TES_TOTAL',
                             'SysMET_SoftTrk_ResoPerp', 'SysMET_SoftTrk_ResoPara',
                             'SysMET_JetTrk_Scale', 'SysMET_SoftTrk_Scale',]
        self._diboson = ['WWPw', 'WZPw', 'ZZPw']
        self._Wjets = ['Wbb', 'Wbc', 'Wbl', 'Wcc', 'Wcl', 'Wl']
        self._Zjets = ['Zbb', 'Zbc', 'Zbl', 'Zcc', 'Zcl', 'Zl', 'ZeeSh221']
        self._top = ['ttbar', 'stop', 'stops', 'stopt', 'stopWt']
        self.root_file_name = root_file_name
        self.region_prefix = region_prefix
        self.histograms = histograms if not load else self._load_histograms()
        self.load = load
        self.store = store
        self._yields = dict()
        self._get_yields()
        if self.store:
            self._save_yields()


    def _systematic(self, name):
        return 'Sys' + name.split('subsmhh_Sys')[1]


    def _pruning(self, yields_process, systematics_list, threshold, total_bkg):
        yields_process_updated = {}
        nominal = yields_process["nEvents"]
        staterror = yields_process["nEventsErr"]
        yields_process_updated["nEvents"] = nominal
        yields_process_updated["nEventsErr"] = staterror
        for systematic in systematics_list:
            systUp = yields_process[systematic + "__1up"]
            systDo = yields_process[systematic + "__1down"]
            # TODO: pruning before merging conflicts with the merging procedure
            #systUpDiffRatio = abs(nominal - systUp)/nominal
            #systDoDiffRatio = abs(nominal - systDo)/nominal
            # Pruning
            #if nominal < 0.02 * total_bkg and systematic in self._shape_systs:
            #    continue
            #if systUpDiffRatio < threshold and systDoDiffRatio < threshold:
            #    continue
            #if abs(systUp - systDo)/nominal < threshold*2:
            #    continue
            ## negative -> ingnore
            #if systUp < 0. or systDo < 0.:
            #    continue
            systVar = [systUp, systDo]
            systVar.sort(reverse=True)
            yields_process_updated[systematic] = systVar

        return yields_process_updated

    def _init_yields_process(self, my_yields_process, keys):
        for key in keys:
            if 'Sys' in key:
                my_yields_process[key] = [0, 0]
            else:
                my_yields_process[key] = 0

    def _sum_yields_process(self, my_yields_process, yields_process):
        for key, value in yields_process.items():
            if 'Sys' in key:
                my_yields_process[key][0] += value[0]
                my_yields_process[key][1] += value[1]
            if 'nEventsErr' in key:
                my_yields_process[key] = sqrt(my_yields_process[key]**2 + value**2)
            if 'nEvents' in key:
                my_yields_process[key] += value

    def _merging(self, yields_mass):
        yields_mass_updated = {}
        yields_diboson = {}
        yields_Wjets = {}
        yields_Zjets = {}
        yields_top = {}
        # HC
        keys = yields_mass['Zbb'].keys()
        self._init_yields_process(yields_diboson, keys)
        self._init_yields_process(yields_Wjets, keys)
        self._init_yields_process(yields_Zjets, keys)
        self._init_yields_process(yields_top, keys)
        for process, yields_process in yields_mass.items():
            if process in self._diboson:
                self._sum_yields_process(yields_diboson, yields_process)
            elif process in self._Wjets:
                self._sum_yields_process(yields_Wjets, yields_process)
            elif process in self._Zjets:
                self._sum_yields_process(yields_Zjets, yields_process)
            elif process in self._top:
                self._sum_yields_process(yields_top, yields_process)
            else:
                yields_mass_updated[process] = yields_process
        yields_mass_updated['diboson'] = yields_diboson
        yields_mass_updated['Wjets'] = yields_Wjets
        yields_mass_updated['Zjets'] = yields_Zjets
        yields_mass_updated['top'] = yields_top
        return yields_mass_updated

    def _pruning_after_merging(self, yields_mass, threshold, total_bkg):
        yields_mass_updated = {}
        for process, yields_process in yields_mass.items():
            nominal = yields_process["nEvents"]
            if nominal == 0: continue
            yields_process_tmp = copy.deepcopy(yields_process)
            for syst, updo in yields_process.items():
                if 'Sys' not in syst: continue
                systUpDiffRatio = abs(nominal - updo[0])/nominal
                systDoDiffRatio = abs(nominal - updo[1])/nominal
                if nominal < 0.02 * total_bkg and syst in self._shape_systs:
                    yields_process_tmp.pop(syst)
                    continue
                if systUpDiffRatio < threshold and systDoDiffRatio < threshold:
                    yields_process_tmp.pop(syst)
                    continue
                if abs(updo[0] - updo[1])/nominal < threshold*2:
                    yields_process_tmp.pop(syst)
                    continue
                # negative -> ignore
                if updo[0] < 0. or updo[1] < 0.:
                    yields_process_tmp.pop(syst)
                    continue
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
                        th1 = root_file.Get(name)
                        nEventsErr = Double(0.)
                        nEvents = th1.IntegralAndError(th1.GetXaxis().GetFirst(),
                                                       th1.GetXaxis().GetLast(),
                                                       nEventsErr)
                        if 'Hhhbbtautau' not in process and 'data' not in process:
                            total_bkg += nEvents
                        del th1
            print("mass {} bkg {}".format(mass, total_bkg))
            for process, name_list in name_dict.items():
                print("-> processing {} / {} ... ".format(mass, process))
                yields_process = {}
                systematics_list = []
                for name in name_list:
                    if "Sys" not in name or process == 'data':
                        th1 = root_file.Get(name)
                        nEventsErr = Double(0.)
                        nEvents = th1.IntegralAndError(th1.GetXaxis().GetFirst(),
                                                       th1.GetXaxis().GetLast(),
                                                       nEventsErr)
                        yields_process.update({"nEvents": float("{0:.6f}".format(nEvents)),
                                               "nEventsErr": float("{0:.6f}".format(nEventsErr))})
                        del th1
                for name in name_list:
                    if 'Sys' in name:
                        syst_name = name.split('__')[0]
                        # fakes are data driven, should only include fakefactor-related systematics
                        if process == 'fakes' and 'SysFF_' not in syst_name:
                            continue
                        systematics_list.append(self._systematic(syst_name))
                        try:
                            th1up = root_file.Get("Systematics/" + syst_name + "__1up")
                            nEventsUp = th1up.Integral()
                        except:
                            nEventsUp = yields_process["nEvents"]
                        try:
                            th1do = root_file.Get("Systematics/" + syst_name + "__1down")
                            nEventsDo = th1do.Integral()
                        except:
                            nominal = yields_process["nEvents"]
                            nEventsDo = 2*nominal - nEventsUp
                        yields_process.update({self._systematic(syst_name) + "__1up": float("{0:.6f}".format(nEventsUp)),
                                               self._systematic(syst_name) + "__1down": float("{0:.6f}".format(nEventsDo))})
                # No negative yields
                if yields_process["nEvents"] < 0:
                    continue
                if process != 'data':
                    yields_process = self._pruning(yields_process, systematics_list, 0.005, total_bkg)
                yields_mass[process] = yields_process
            yields_mass = self._merging(yields_mass)
            yields_mass = self._pruning_after_merging(yields_mass, 0.005, total_bkg)
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
