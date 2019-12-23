from __future__ import print_function

import sys

sys.path.insert(0, '/Users/bowen/PycharmProjects/SampleBuilder/')
from pprint import pprint
from ROOT import gROOT
from sample_builder.sbhistograms import SBHistograms

print("My ROOT version is {}".format(gROOT.GetVersion()))


def utest_histograms(debug=False):
    root_file_name = "/Users/bowen/Documents/work/Boosted/root_files/submitDir_v10_w25_mc16ade.root"
    region_prefix = "2tag2pjet_0ptv_SRLRJwindow"
    #masses = [1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000]
    masses = [1000, 1200]
    pickle_file_name = '/Users/bowen/PycharmProjects/SampleBuilder/pickle_files/histograms.dictionary'

    sbh = SBHistograms(root_file_name, region_prefix, masses)
    sbh.disc = "subsmhh"
    sbh.signal_prefix = "Hhhbbtautau"
    sbh.masscut = {
        "1000": "",
        "1200": "",
        "1400": "",
        "1600": "MHH900",
        "1800": "MHH900",
        "2000": "MHH900",
        "2500": "MHH1200",
        "3000": "MHH1200",
    }
    sbh.save_histograms(pickle_file_name)

    if debug:
        pprint(sbh.histograms)


utest_histograms(False)
