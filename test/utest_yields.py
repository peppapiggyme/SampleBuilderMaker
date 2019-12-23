import sys
sys.path.insert(0, '/Users/bowen/PycharmProjects/SampleBuilderMaker/')
from pprint import pprint
from ROOT import gROOT
print(gROOT.GetVersion())
from sbmaker.sbyields import SBYields

filename = "/Users/bowen/Documents/work/Boosted/root_files/submitDir_v10_w23_mc16ade.root"
prefix = "1tag2pjet_0ptv_SRMHHX"
binning = [0., 4000.]
useCache = True

sby = SBYields(filename, prefix, binning, None, useCache, True)

#pprint(sby.yields)

## EOF
