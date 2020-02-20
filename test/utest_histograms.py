from __future__ import print_function
from pprint import pprint
from sample_builder.sbhistograms import SBHistograms

from ROOT import gROOT

print("My ROOT version is {}".format(gROOT.GetVersion()))


def utest_histograms(debug=False):
    root_file_name = "../root_files/submitDir_v10_mc16ade.root"
    region_prefix = "2tag2pjet_0ptv_SRLRJwindow"
    masses = [1000, 1100, 1200, 1400, 1600, 1800, 2000, 2500, 3000]
    pickle_file_name = '../pickle_files/histograms.data'

    sbh = SBHistograms(root_file_name, region_prefix, masses)
    sbh.disc = "subsmhh"
    sbh.signal_prefix = "Hhhbbtautau"
    sbh.masscut = {
        "1000": "",
        "1100": "",
        "1200": "",
        "1400": "",
        "1600": "MHH900",
        "1800": "MHH900",
        "2000": "MHH900",
        "2500": "MHH1200",
        "3000": "MHH1200",
    }
    sbh.save_data(pickle_file_name)

    if debug:
        pprint(sbh.data)


utest_histograms(False)
