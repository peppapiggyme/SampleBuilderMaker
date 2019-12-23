from __future__ import print_function

from ROOT import gROOT
from ROOT import kGray, kRed, kPink, kViolet, kBlue, kAzure, kGreen, \
    kOrange

print(gROOT.GetVersion())
## EOF
import pickle
from math import sqrt

cache_name = '/Users/bowen/PycharmProjects/SampleBuilder/pickle_files/yields.dictionary'
yields = None
with open(cache_name, 'rb') as yields_pickle:
    yields = pickle.load(yields_pickle)

masses = [1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000]
signal_prefix = "Hhhbbtautau"

color_dict = {"Zbb": kAzure, "Zbc": kAzure, "Zbl": kAzure,
              "Zcc": kAzure, "Zcl": kBlue, "Zl": kBlue,
              "Wbb": kGreen, "Wbc": kGreen, "Wbl": kGreen,
              "Wcc": kGreen, "Wcl": kGreen, "Wl": kGreen,
              "ttbar": kOrange, "stop": kOrange, "stopWt": kOrange,
              "ZZPw": kGray, "WZPw": kGray, "WWPw": kGray, "fakes": kPink,
              "Zjets": kAzure, "Wjets": kGreen, "top": kOrange, "diboson": kGray,
              "$Z\\tau\\tau$+HF": kAzure, "$Z\\tau\\tau$+LF": kBlue, "$W$+jets": kGreen, "$Zee$": kViolet,
              "Zhf": kAzure, "Zlf": kBlue, "Zee": kViolet,
              signal_prefix + "1000": kRed, signal_prefix + "1200": kRed,
              signal_prefix + "1400": kRed, signal_prefix + "1600": kRed,
              signal_prefix + "1800": kRed, signal_prefix + "2000": kRed,
              signal_prefix + "2500": kRed, signal_prefix + "3000": kRed,
              # Add your new processes here
              }


def utest():
    for mass in masses:
        print("@ {}: ".format(mass))
        print_info(mass)
        print_syst_table(mass)


def sum_of_bkg(yields_mass):
    s = 0
    for process, yields_process in yields_mass.items():
        if process != "data" and signal_prefix not in process:
            # print(process+', ')
            s += sum(yields_process["nEvents"])
    return s


def sqrt_sum_of_bkg_error(yields_mass):
    s = 0
    for process, yields_process in yields_mass.items():
        if process != "data" and signal_prefix not in process:
            # print(process+', ')
            s += sum([e ** 2 for e in yields_process["nEventsErr"]])
    return sqrt(s)


def print_info(mass):
    mass = str(mass)
    yields_mass = yields[mass]
    # pprint(yields_mass)
    for process, yields_process in sorted(yields_mass.items(), key=lambda x: sum(x[1]["nEvents"]), reverse=True):
        if process == 'data': continue
        if signal_prefix in process: continue
        # print("-> {} / Colour: {}".format(process, color_dict[process]))
        noms = yields_process["nEvents"]
        nominal = sum(noms)
        errors = yields_process["nEventsErr"]
        staterror = sqrt(sum([e ** 2 for e in errors]))
        # print("  nEvents (StatError): {} ({})".format(noms, errors))
        for key, values in yields_process.items():
            if 'Sys' not in key: continue
            ups = values[0]
            downs = values[1]
            # systUpRatio = [u / n if n != 0. else float(1.) for u, n in zip(ups, noms)]
            # systDoRatio = [d / n if n != 0. else float(1.) for d, n in zip(downs, noms)]
            # if sum(r > 2 for r in systUpRatio) > 0 or sum(r < 0.5 for r in systDoRatio) > 0 or sum(
            #        r <= 1 for r in systUpRatio) > sum(r >= 1 for r in systDoRatio):
            #    print("  {} UP {} DO {}".format(key, systUpRatio, systDoRatio))
        print("\\multicolumn{1}" + "{l|}" + "{" + "{}".format(
            process) + "}" + "	&  $ {:.3f} \\pm {:.3f} $ \\\\".format(nominal, staterror))
        if signal_prefix in process:
            print("  This is signal !")
            pass
    print('\\hline')
    print("\\multicolumn{1}" + "{l|}" + "{Total bkg}" + "	&  $ {:.3f} \\pm {:3f} $ \\\\".format(
        sum_of_bkg(yields_mass), sqrt_sum_of_bkg_error(yields_mass)))
    for process, yields_process in yields_mass.items():
        noms = yields_process["nEvents"]
        nominal = sum(noms)
        errors = yields_process["nEventsErr"]
        staterror = sqrt(sum([e ** 2 for e in errors]))
        if signal_prefix in process:
            process = 'X' + str(mass)
            print("\\multicolumn{1}" + "{l|}" + "{" + "{}".format(
                process) + "}" + "	&  $ {:.3f} \\pm {:.3f} $ \\\\".format(nominal, staterror))
    print('\\hline')


def print_syst_table(mass):
    syst_table = dict()
    mass = str(mass)
    yields_mass = yields[mass]
    total_bkg = sum_of_bkg(yields_mass)
    for process, yields_process in yields_mass.items():
        if process == 'data' or signal_prefix in process:
            continue
        for key, value in yields_process.items():
            if 'ATLAS' not in key: continue
            assert len(value[0]) == len(value[1])
            syst_table[key] = [total_bkg, total_bkg]  # initilize
    for process, yields_process in yields_mass.items():
        if process == 'data' or signal_prefix in process:
            continue
        nominal = sum(yields_process["nEvents"])
        for key, value in yields_process.items():
            if 'ATLAS' not in key: continue
            syst_table[key][0] += sum(value[0]) - nominal  # sum
            syst_table[key][1] += sum(value[1]) - nominal  # sum
    for key, value in sorted(syst_table.items(), key=lambda x: x[1][0] - x[1][1], reverse=True):
        print('{} & {:.2f}/{:.2f} \\\\'.format(key.replace("ATLAS_", "").replace("_hadhad", ""),
                                               (value[0] / total_bkg - 1) * 100, (value[1] / total_bkg - 1) * 100))


utest()
