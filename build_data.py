#!/usr/bin/env python
# encoding: utf-8
"""
build_data.py
~~~~~~~~~

Main function to build yield data from Reader output
Output is the `yield.data`

"""

# IMPORT
from __future__ import print_function

import argparse

from pprint import pprint
from sample_builder.sbhistograms import SBHistograms
from sample_builder.sbyields import SBYields
from utils.logging_tools import get_logger

from ROOT import gROOT

print("My ROOT version is {}".format(gROOT.GetVersion()))


def build_data(args):
    # logger
    logger = get_logger("MAIN", "INFO")

    # PRE-DEFINITIONS
    region_prefix = "2tag2pjet_0ptv_SRLRJwindow"
    disc = "subsmhh"
    signal_prefix = "Hhhbbtautau"
    masses = [1000, 1100, 1200, 1400, 1600, 1800, 2000, 2500, 3000]
    binning = [0., 4000.]

    # histograms data
    logger.info("# 1 - Histograms")
    sbh = SBHistograms(args.input, region_prefix, masses)
    sbh.disc = disc
    sbh.signal_prefix = signal_prefix
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
    sbh.save_data(args.histograms)

    # yields data
    logger.info("# 2 - Yields")
    sby = SBYields(args.input, region_prefix, masses, binning)

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
    sby.VH  = ['WHtautau', 'ZHtautau', 'qqWlvH125', 'qqZllH125', 'qqZvvH125', 'ggZllH125', 'ggZvvH125']
    
    sby.ignore = ['ttH']

    sby.others = sby.diboson + sby.Wjets + sby.Zee + sby.top
    sby.for_histfitter = True
    sby.do_merging = True

    sby.disc = disc
    sby.signal_prefix = signal_prefix
    sby.cache_name = args.histograms

    sby.save_data(args.yields)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default="root_files/submitDir_v10_mc16ade.root",
                        help="CxAODReader output root file (merged by bohadd)")
    parser.add_argument("--histograms", default="pickle_files/histograms.data",
                        help="Output histograms data name")
    parser.add_argument("--yields", default="pickle_files/yields.data",
                        help="Output yields data name")

    args = parser.parse_args()

    build_data(args)
