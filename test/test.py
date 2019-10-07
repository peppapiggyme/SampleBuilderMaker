from ROOT import gROOT
from ROOT import kBlack, kWhite, kGray, kRed, kPink, kMagenta, kViolet, kBlue, kAzure, kCyan, kTeal, kGreen, \
        kSpring, kYellow, kOrange
print(gROOT.GetVersion())
from pprint import pprint
## EOF
import pickle
yields = None
with open('/Users/bowen/PycharmProjects/SampleBuilderMaker/pickle_files/yields.dictionary', 'rb') as yields_pickle:
    yields = pickle.load(yields_pickle)


color_dict = {"Zjets": kAzure,
              "Wjets": kGreen,
              "top": kOrange,
              "diboson": kGray,
              "fakes": kPink,
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

def print_info(mass):
    mass = str(mass)
    yields_mass = yields[mass]
    #pprint(yields_mass)
    for process, yields_process in yields_mass.items():
        if process == 'data': continue
        print("-> {} / Colour: {}".format(process, color_dict[process]))
        nominal = yields_process["nEvents"]
        staterror = yields_process["nEventsErr"]
        print("  nEvents (StatError): {} ({})".format(nominal, staterror))
        for key, value in yields_process.items():
            if 'Sys' not in key: continue
            systUpRatio = value[0] / nominal
            systDoRatio = value[1] / nominal
            if systUpRatio > 2 or systDoRatio < 0.5:
                print("  {} UP {} DO {}".format(key, systUpRatio, systDoRatio))
        if 'Hhhbbtautau' in process:
            print("  This is signal !")
            pass

    print("number of fake data {}".format(sum_of_bkg(yields_mass)))

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
    for key, value in sorted(syst_table.items(), key = lambda x : x[1][0]-x[1][1], reverse=True):
        #print("{} & {:.2f} / {:.2f} / {:.2f}".format(key, value[0], value[1], total_bkg))
        print('{} & {:.2f}/{:.2f} \\\\'.format(key, (value[0] / total_bkg - 1) * 100, (value[1] / total_bkg - 1) * 100))

for mass in [1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000]:
    print("@ {}: ".format(mass))
    print_info(mass)
    #print_syst_table(mass)
