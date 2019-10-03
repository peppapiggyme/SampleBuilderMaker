# IMPORT
from ROOT import TFile, TH1F, TDirectory, gDirectory, Double


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
            systUpDiffRatio = abs(nominal - systUp)/nominal
            systDoDiffRatio = abs(nominal - systDo)/nominal
            # Pruning
            if nominal < 0.02 * total_bkg and systematic in self._shape_systs:
                continue
            if abs(staterror / nominal) > 0.5:
                continue
            if systUpDiffRatio < threshold and systDoDiffRatio < threshold:
                continue
            # cleaning acceptance effect of shape systs
            # TODO: Low statistic -> should merge samples -> stablise calculation
            if abs(systUp - systDo)/nominal < threshold*2:
                continue
            # negative -> ingnore
            if systUp < 0. or systDo < 0.:
                continue
            systVar = [systUp, systDo]
            systVar.sort(reverse=True)
            yields_process_updated[systematic] = systVar

        return yields_process_updated


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
                        th1up = root_file.Get("Systematics/" + syst_name + "__1up")
                        nEventsUp = th1up.Integral()
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
