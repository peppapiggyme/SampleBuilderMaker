from __future__ import print_function

import sys

sys.path.insert(0, '/Users/bowen/PycharmProjects/SampleBuilder/')
from pprint import pprint
from ROOT import gROOT
from sample_builder.sbyields import SBYields

print( "My ROOT version is {}".format(gROOT.GetVersion()) )

def utest_yields(debug=False):
    root_file_name = "/Users/bowen/Documents/work/Boosted/root_files/submitDir_v10_w25_mc16ade.root"
    region_prefix = "2tag2pjet_0ptv_SRLRJwindow"
    binning = [0., 4000.]  # One bin
    cache_name = '/Users/bowen/PycharmProjects/SampleBuilder/pickle_files/histograms.dictionary'
    pickle_file_name = '/Users/bowen/PycharmProjects/SampleBuilder/pickle_files/yields.dictionary'

    sby = SBYields(root_file_name, region_prefix, binning)

    # sby.shape_systs = ['SysFATJET_Medium_JET_Comb_Baseline_Kin',
    #                  'SysFATJET_Medium_JET_Comb_TotalStat_Kin',
    #                  'SysFATJET_Medium_JET_Comb_Modelling_Kin',
    #                  'SysFATJET_Medium_JET_Comb_Tracking_Kin',
    #                  'SysFATJET_JER', 'SysFATJET_JMR',
    #                  'SysTAUS_TRUEHADDITAU_EFF_JETID_TOTAL',
    #                  'SysTAUS_TRUEHADDITAU_SME_TES_TOTAL',
    #                  'SysMET_SoftTrk_ResoPerp', 'SysMET_SoftTrk_ResoPara',
    #                  'SysMET_JetTrk_Scale', 'SysMET_SoftTrk_Scale',
    #                  'SysPRW_DATASF', ]

    sby.diboson = ['WWPw', 'WZPw', 'ZZPw']
    sby.Wjets = ['Wbb', 'Wbc', 'Wbl', 'Wcc', 'Wcl', 'Wl']
    sby.Zhf = ['Zbb', 'Zbc', 'Zbl', 'Zcc']
    sby.Zlf = ['Zcl', 'Zl']
    sby.Zee = ['ZeeSh221']
    sby.top = ['ttbar', 'stop', 'stops', 'stopt', 'stopWt', 'ttbar_allhad', 'ttbar_nonallhad']
    sby.for_histfitter = True
    sby.do_merging = True

    sby.disc = "subsmhh"
    sby.signal_prefix = "Hhhbbtautau"

    sby.save_yields(cache_name, pickle_file_name)

    if debug:
        pprint(sby.yields)

utest_yields(False)
