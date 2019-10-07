import sys
sys.path.insert(0, '/Users/bowen/PycharmProjects/SampleBuilderMaker/')
from pprint import pprint
from ROOT import gROOT
print(gROOT.GetVersion())
from sbmaker.sbhistograms import SBHistograms

filename = "/Users/bowen/Documents/work/Boosted/root_files/submitDir_v10_w20_mc16ade.root"
prefix = "2tag2pjet_0ptv_SRMHHX"
masses = [1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000]

sbh = SBHistograms(filename, prefix, masses, True)

# pprint(sbh.histograms)

## EOF
