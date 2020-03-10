from __future__ import print_function
from pprint import pprint
from sample_builder.sbyields import SBYields

from ROOT import gROOT

print( "My ROOT version is {}".format(gROOT.GetVersion()) )

def utest_yields(debug=False):
    root_file_name = "../root_files/submitDir_v10_mc16ade.root"
    region_prefix = "2tag2pjet_0ptv_SRLRJwindow"
    masses = [1000, 1100, 1200, 1400, 1600, 1800, 2000, 2500, 3000]
    binning = [0., 4000.]  # One bin
    pickle_file_name = '../pickle_files/yields.data'

    sby = SBYields(root_file_name, region_prefix, masses, binning)

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
    sby.VH  = ['VHtautau', 'WHtautau', 'ZHtautau', 'qqWlvH125', 'qqZllH125', 'qqZvvH125', 'ggZllH125', 'ggZvvH125']
    
    sby.ignore = ['ttH', 'Hhhbbtautau1000lephad', 'Hhhbbtautau2000lephad']

    sby.others = sby.diboson + sby.Wjets + sby.Zee + sby.top
    
    sby.for_histfitter = True
    sby.do_merging = True

    sby.disc = "subsmhh"
    sby.signal_prefix = "Hhhbbtautau"
    sby.cache_name = '../pickle_files/histograms.data'

    sby.save_data(pickle_file_name)

    if debug:
        pprint(sby.data)

utest_yields(False)
