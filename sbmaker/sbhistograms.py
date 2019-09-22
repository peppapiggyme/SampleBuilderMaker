# IMPORT
from ROOT import TFile, TH1F, TDirectory, gDirectory

# Singleton: one ROOT file -> one instance (singleton not checked)
# WARN: HC in _get_sample_list(mass)!

class SBHistograms():

    def __init__(self, root_file_name, region_prefix, masses, store):
        self._histograms    = dict()
        self.root_file_name = root_file_name
        self.region_prefix  = region_prefix
        self.masses         = masses
        self.store          = store
        self._get_histograms()
        if self.store:
            self._save_histograms()


    def _get_histograms_mass(self, mass):
        name_list = list()
        print("Getting list of region {} ...".format(self.region_prefix+str(mass)))
        root_file = TFile(self.root_file_name)
        hash = gDirectory.GetListOfKeys()
        iter = hash.MakeIterator()
        key = iter.Next()
        while key:
            name = key.ReadObj().GetName()
            key = iter.Next()
            if self.region_prefix+str(mass)+"_subsmhh" in name:
                if "Hhhbbtautau" in name and "Hhhbbtautau"+str(mass) not in name: continue
                if "Hhhbbtautau"+str(mass)+"Py8" in name: continue
                name_list.append(name)
        root_file.cd("Systematics")
        hash = gDirectory.GetListOfKeys()
        iter = hash.MakeIterator()
        key = iter.Next()
        while key:
            name = key.ReadObj().GetName()
            key = iter.Next()
            if self.region_prefix+str(mass)+"_subsmhh" in name:
                if "Hhhbbtautau" in name and "Hhhbbtautau"+str(mass) not in name: continue
                if "Hhhbbtautau"+str(mass)+"Py8" in name: continue
                if "data" in name and "subsmhh_Sys" in name: continue
                if name.split('_Sys')[0] not in name_list: continue # some inconsistency of nomial and systs
                name_list.append(name)
        root_file.Close()
        return name_list


    def _process(self, name):
        return name.split('_')[0]

    def _get_histograms(self):
        for mass in self.masses:
            name_dict = dict()
            process_list = list()
            name_list = self._get_histograms_mass(mass)
            for name in name_list:
                process_list.append(self._process(name))
            process_list = list(set(process_list))
            print(mass, "  ", process_list)
            for process in process_list:
                name_dict[process] = [h for h in name_list if process in h]
            self._histograms[str(mass)] = name_dict


    @property
    def histograms(self):
        return self._histograms


    def _save_histograms(self):
        import pickle
        with open('/Users/bowen/PycharmProjects/SampleBuilderMaker/pickle_files/histograms.dictionary', 'wb') as histograms_pickle:
            pickle.dump(self._histograms, histograms_pickle)
