from ROOT import gROOT
from ROOT import kBlack, kWhite, kGray, kRed, kPink, kMagenta, kViolet, kBlue, kAzure, kCyan, kTeal, kGreen, \
        kSpring, kYellow, kOrange
print(gROOT.GetVersion())
from pprint import pprint
## EOF
import pickle
from math import sqrt

yields = None
with open('/Users/bowen/PycharmProjects/SampleBuilderMaker/pickle_files/yields.dictionary', 'rb') as yields_pickle:
    yields = pickle.load(yields_pickle)

color_dict = {"Zbb": kAzure, "Zbc": kAzure, "Zbl": kAzure,
              "Zcc": kAzure, "Zcl": kBlue, "Zl": kBlue,
              "Wbb": kGreen, "Wbc": kGreen, "Wbl": kGreen,
              "Wcc": kGreen, "Wcl": kGreen, "Wl": kGreen,
              "ttbar": kOrange, "stop": kOrange, "stopWt": kOrange,
              "ZZPw": kGray, "WZPw": kGray, "WWPw": kGray, "fakes": kPink,
              "Zjets": kAzure, "Wjets": kGreen, "top": kOrange, "diboson": kGray, "fakes": kPink,
              "$Z\\tau\\tau$+HF": kAzure, "$Z\\tau\\tau$+LF": kBlue, "$W$+jets": kGreen, "$Zee$": kViolet,
              "Zhf": kAzure, "Zlf": kBlue, "Zee": kViolet,
              "Hhhbbtautau1000": kRed, "Hhhbbtautau1200": kRed,
              "Hhhbbtautau1400": kRed, "Hhhbbtautau1600": kRed,
              "Hhhbbtautau1800": kRed, "Hhhbbtautau2000": kRed,
              "Hhhbbtautau2500": kRed, "Hhhbbtautau3000": kRed,
              }


def sum_of_bkg(yields_mass):
    sum = 0
    for process, yields_process in yields_mass.items():
        if process != "data" and "Hhhbbtautau" not in process:
            #print(process+', ')
            sum += yields_process["nEvents"]
    return sum

def sqrt_sum_of_bkg_error(yields_mass):
    sum = 0
    for process, yields_process in yields_mass.items():
        if process != "data" and "Hhhbbtautau" not in process:
            # print(process+', ')
            sum += yields_process["nEventsErr"]**2
    return sqrt(sum)

def print_info(mass):
    mass = str(mass)
    yields_mass = yields[mass]
    #pprint(yields_mass)
    for process, yields_process in sorted(yields_mass.items(), key=lambda x: x[1]["nEvents"], reverse=True):
        if process == 'data': continue
        if 'Hhhbbtautau' in process: continue
        print("-> {} / Colour: {}".format(process, color_dict[process]))
        nominal = yields_process["nEvents"]
        staterror = yields_process["nEventsErr"]
        print("  nEvents (StatError): {} ({})".format(nominal, staterror))
        for key, value in yields_process.items():
            if 'Sys' not in key: continue
            systUpRatio = value[0] / nominal
            systDoRatio = value[1] / nominal
            if systUpRatio > 2 or systDoRatio < 0.5 or systUpRatio <= 1 or systDoRatio >= 1 or True:
                print("  {} UP {} DO {}".format(key, systUpRatio, systDoRatio))
        print("\\multicolumn{1}" + "{l|}" + "{" + "{}".format(process) + "}"+"	&  $ {:.3f} \\pm {:.3f} $ \\\\".format(nominal, staterror))
        if 'Hhhbbtautau' in process:
            print("  This is signal !")
            pass
    print('\\hline')
    print("\\multicolumn{1}"+"{l|}"+"{Total bkg}"+"	&  $ {:.3f} \\pm {:3f} $ \\\\".format(sum_of_bkg(yields_mass), sqrt_sum_of_bkg_error(yields_mass)))
    for process, yields_process in yields_mass.items():
       nominal = yields_process["nEvents"]
       staterror = yields_process["nEventsErr"]
       if 'Hhhbbtautau' in process:
           process = 'X'+str(mass)
           print("\\multicolumn{1}" + "{l|}" + "{" + "{}".format(process) + "}" + "	&  $ {:.3f} \\pm {:.3f} $ \\\\".format(nominal, staterror))
    print('\\hline')

def print_syst_table(mass):
    syst_table = dict()
    mass = str(mass)
    yields_mass = yields[mass]
    total_bkg = sum_of_bkg(yields_mass)
    for process, yields_process in yields_mass.items():
        if process == 'data' or 'Hhhbbtautau' in process:
            continue
        for key, _ in yields_process.items():
            if 'Sys' not in key: continue
            syst_table[key] = [total_bkg, total_bkg] # initilize
    for process, yields_process in yields_mass.items():
        if process == 'data' or 'Hhhbbtautau' in process:
            continue
        nominal = yields_process["nEvents"]
        for key, value in yields_process.items():
            if 'Sys' not in key: continue
            syst_table[key][0] += value[0] - nominal  # sum
            syst_table[key][1] += value[1] - nominal  # sum
    for key, value in sorted(syst_table.items(), key=lambda x: x[1][0]-x[1][1], reverse=True):
        #print("{} & {:.2f} / {:.2f} / {:.2f}".format(key, value[0], value[1], total_bkg))
        print('{} & {:.2f}/{:.2f} \\\\'.format(key, (value[0] / total_bkg - 1) * 100, (value[1] / total_bkg - 1) * 100))

for mass in [1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000]:
    print("@ {}: ".format(mass))
    print_info(mass)
    #print_syst_table(mass)
