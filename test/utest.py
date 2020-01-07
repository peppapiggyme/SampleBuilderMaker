from __future__ import print_function

from ROOT import gROOT
from ROOT import kGray, kRed, kPink, kViolet, kBlue, kAzure, kGreen, kOrange

print("My ROOT version is {}".format(gROOT.GetVersion()))

import pickle
from math import sqrt

BLIND = False

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

syst_mapping = {
    'Luminosity and pile-up': ['ATLAS_Lumi_Run2_hadhad',
                               'ATLAS_PRW_DATASF_hadhad'],
    'MC statistics': ['stat_SR_subsmhh_bin_0'],
    'Large-R jet and MET': ['ATLAS_FATJET_JER_hadhad',
                            'ATLAS_FATJET_JMR_hadhad',
                            'ATLAS_FATJET_Medium_JET_Comb_Baseline_Kin_hadhad',
                            'ATLAS_FATJET_Medium_JET_Comb_Modelling_Kin_hadhad',
                            'ATLAS_FATJET_Medium_JET_Comb_Tracking_Kin_hadhad',
                            'ATLAS_FATJET_Medium_JET_Comb_TotalStat_Kin_hadhad'],
    'Di-tau': ['ATLAS_DiTauSF_Stat_hadhad',
               'ATLAS_DiTauSF_Syst_hadhad',
               'ATLAS_TAUS_TRUEHADDITAU_EFF_JETID_TOTAL_hadhad',
               'ATLAS_TAUS_TRUEHADDITAU_SME_TES_TOTAL_hadhad'],
    'Flavour tagging': ['ATLAS_FT_EFF_Eigen_B_0_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_B_1_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_B_2_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_C_0_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_C_1_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_C_2_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_C_3_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_Light_0_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_Light_1_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_Light_2_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_Eigen_Light_3_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_extrapolation_AntiKtVR30Rmax4Rmin02TrackJets_hadhad',
                        'ATLAS_FT_EFF_extrapolation_from_charm_AntiKtVR30Rmax4Rmin02TrackJets_hadhad'],
    'Background estimation': ['ATLAS_FF_1BTAG_SIDEBAND_Syst_hadhad',
                              'ATLAS_FF_Stat_hadhad',
                              'ATLAS_FF_Transition_Btag_hadhad',
                              'ATLAS_FF_Transition_Sign_hadhad',
                              'ATLAS_TTBAR_YIELD_UPPER_hadhad',
                              'ATLAS_ZhfSF_Stat_hadhad',
                              'ATLAS_ZhfSF_Syst_hadhad'],
    'Signal Acceptance': ['ATLAS_SigAcc_hadhad']
}

stat_error_bkg = {
    "1000": 0.3271,
    "1200": 0.3271,
    "1400": 0.3271,
    "1600": 0.2622,
    "1800": 0.2622,
    "2000": 0.2622,
    "2500": 0.3035,
    "3000": 0.3035,
}

stat_error_sig = {
    "1000": 0.024,
    "1200": 0.017,
    "1400": 0.013,
    "1600": 0.013,
    "1800": 0.012,
    "2000": 0.012,
    "2500": 0.014,
    "3000": 0.018,
}

sigacc_error = {
    "1000": 0.24,
    "1200": 0.033,
    "1400": 0.036,
    "1600": 0.028,
    "1800": 0.041,
    "2000": 0.041,
    "2500": 0.033,
    "3000": 0.024,
}

# up
ttbar_error = {
    "1000": 0.095,
    "1200": 0.095,
    "1400": 0.095,
    "1600": 0.1076,
    "1800": 0.1076,
    "2000": 0.1076,
    "2500": 0.3866,
    "3000": 0.3866,
}

LumiError = 0.017


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
    print("\\multicolumn{1}" + "{l|}" + "{Total bkg}" + "	&  $ {:.3f} \\pm {:.3f} $ \\\\".format(
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
        if not BLIND and process == 'data':
            print("\\multicolumn{1}" + "{l|}" + "{Data}   " + "    &  $ {:.3f} \\pm {:.3f} $ \\\\".format(
                nominal, staterror))
    print('\\hline')


def print_syst_table(mass):
    syst_table = dict()
    mass = str(mass)
    yields_mass = yields[mass]
    total_bkg = sum_of_bkg(yields_mass)
    n_signal = sum(yields_mass[signal_prefix + mass]["nEvents"])
    for process, yields_process in yields_mass.items():
        if process == 'data':
            continue
        for key, value in yields_process.items():
            if 'ATLAS' not in key: continue
            assert len(value[0]) == len(value[1])
            syst_table[key] = [total_bkg, total_bkg, n_signal, n_signal]  # initialize
    for process, yields_process in yields_mass.items():
        if process == 'data' or signal_prefix in process:
            continue
        nominal = sum(yields_process["nEvents"])
        for key, value in yields_process.items():
            if 'ATLAS' not in key: continue
            syst_table[key][0] += sum(value[0]) - nominal  # sum
            syst_table[key][1] += sum(value[1]) - nominal  # sum
    for process, yields_process in yields_mass.items():
        if signal_prefix not in process:
            continue
        nominal = sum(yields_process["nEvents"])
        for key, value in yields_process.items():
            if 'ATLAS' not in key: continue
            syst_table[key][2] += sum(value[0]) - nominal  # sum
            syst_table[key][3] += sum(value[1]) - nominal  # sum

    syst_table_perc = {}
    for key, value in sorted(syst_table.items(), key=lambda x: abs(x[1][0] - x[1][1]), reverse=True):
        a_bkg = (value[0] / total_bkg - 1)
        b_bkg = (value[1] / total_bkg - 1)
        a_sig = (value[2] / n_signal - 1)
        b_sig = (value[3] / n_signal - 1)
        p_bkg = a_bkg if a_bkg > 0 else b_bkg
        n_bkg = b_bkg if a_bkg > 0 else a_bkg
        p_sig = a_sig if a_sig > 0 else b_sig
        n_sig = b_sig if a_sig > 0 else a_sig
        # print the very detailed table
        # print('{} & {:.2f}/{:.2f} & {:.2f}/{:.2f} \\\\'.format(key.replace("ATLAS_", "").replace("_hadhad", ""),
        #                                                        p_bkg * 100, n_bkg * 100, p_sig * 100, n_sig * 100
        #                                                        ))
        syst_table_perc[key] = [p_bkg, n_bkg, p_sig, n_sig]

    # Table with grouped systematics
    mytotal = [0, 0, 0, 0]
    for key, syst_list in syst_mapping.items():
        mysum = [0, 0, 0, 0]
        if key == 'MC statistics':
            mysum = [stat_error_bkg[mass], stat_error_bkg[mass], stat_error_sig[mass], stat_error_sig[mass]]
        elif key == 'Signal Acceptance':
            mysum = [0, 0, sigacc_error[mass], sigacc_error[mass]]
        else:
            for syst in syst_list:
                try:
                    mysum = [(sqrt(mysum[i] ** 2 + syst_table_perc[syst][i] ** 2)) for i in range(4)]
                except:
                    # uncomment tfor debugging
                    # print("{} not in yield data file, will use hardcoded data".format(syst))
                    if syst == 'ATLAS_Lumi_Run2_hadhad':
                        mysum = [(sqrt(mysum[i] ** 2 + LumiError ** 2)) for i in range(4)]
                    if syst == 'ATLAS_TTBAR_YIELD_UPPER_hadhad':
                        mysum[0] = sqrt(mysum[0] ** 2 + ttbar_error[mass] ** 2)
                    if syst == 'ATLAS_FF_1BTAG_SIDEBAND_Syst_hadhad':
                        # uncomment tfor debugging
                        # print('TODO: {}'.format(syst))
                        pass

        print("{} & {:.1f}/{:.1f} & {:.1f}/{:.1f} \\\\".format(
            key, *tuple([mysum[i]*100 if i % 2 == 0 else mysum[i]*100*(-1) for i in range(4)])))
        mytotal = [(sqrt(mytotal[i] ** 2 + mysum[i] ** 2)) for i in range(4)]

    print("Total & {:.1f}/{:.1f} & {:.1f}/{:.1f} \\\\".format(
        *tuple([mytotal[i] * 100 if i % 2 == 0 else mytotal[i] * 100 * (-1) for i in range(4)])))


utest()
