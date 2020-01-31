import copy
import pickle

BLIND = False

yields = None
with open('yields.dictionary', 'rb') as yields_pickle:
    yields = pickle.load(yields_pickle)

# my configuration
my_disc = "subsmhh"  # discriminant variable (HC: if set to "cuts", will force to use one bin!)
signal_prefix = "Hhhbbtautau"

# do systematic or not
no_syst = False
stat_config = True
if no_syst:
    stat_config = False
stat_only = False
if stat_only:
    stat_config = True
use_mcstat = True
dict_syst_check = {
    "other": False,  # other = lumi and PRW
    "jetmet": False,  # FATJET_*, MET_*
    "ditau": False,  # TAU_*, DiTauSF_*
    "ftag": False,  # FT_*
    "bkg": False,  # FF_*, TTBAR_*, ZhfSF_*
    "sig": False,  # SIG_*
}

# binning (for HistFactory)
my_nbins = 1
my_xmin = 0.5
my_xmax = my_xmin + my_nbins

syst_type = "overallSys" if my_nbins == 1 else "overallNormHistoSys"

unc_sig_acc = {
    "1000": 0.24,
    "1200": 0.033,
    "1400": 0.036,
    "1600": 0.028,
    "1800": 0.041,
    "2000": 0.041,
    "2500": 0.033,
    "3000": 0.024,
}

unc_ttbar_v1 = {
    "1000": 12120.0,
    "1200": 12120.0,
    "1400": 12120.0,
    "1600": 12120.0,
    "1800": 12120.0,
    "2000": 12120.0,
    "2500": 12120.0,
    "3000": 12120.0,
}

unc_ttbar_v2 = {
    "1000": 4400.0,
    "1200": 4400.0,
    "1400": 4400.0,
    "1600": 3600.0,
    "1800": 3600.0,
    "2000": 3600.0,
    "2500": 1500.0,
    "3000": 1500.0,
}

unc_ttbar_v3 = {
    "1000": 7027.0,
    "1200": 7027.0,
    "1400": 7027.0,
    "1600": 5713.0,
    "1800": 5713.0,
    "2000": 5713.0,
    "2500": 2375.0,
    "3000": 2375.0,
}

unc_ttbar = unc_ttbar_v1


# shape_systs = ['SysFATJET_Medium_JET_Comb_Baseline_Kin',
#                'SysFATJET_Medium_JET_Comb_TotalStat_Kin',
#                'SysFATJET_Medium_JET_Comb_Modelling_Kin',
#                'SysFATJET_Medium_JET_Comb_Tracking_Kin',
#                'SysFATJET_JER', 'SysFATJET_JMR',
#                'SysTAUS_TRUEHADDITAU_EFF_JETID_TOTAL',
#                'SysTAUS_TRUEHADDITAU_SME_TES_TOTAL',
#                'SysMET_SoftTrk_ResoPerp', 'SysMET_SoftTrk_ResoPara',
#                'SysMET_JetTrk_Scale', 'SysMET_SoftTrk_Scale',
#                'SysPRW_DATASF', ]


def sum_of_bkg(yields_mass):
    sum = [0. for _ in range(my_nbins)]
    for process, yields_process in yields_mass.items():
        if process != "data" and signal_prefix not in process:
            old_values = copy.deepcopy(sum)
            sum = [o + v for o, v in zip(old_values, yields_process["nEvents"])]
            del old_values
    return sum


def impact_check_continue(dict_syst_check, key):
    ipc = False
    if dict_syst_check["other"]:
        if key.startswith("ATLAS_PRW_DATASF") or key.startswith("ATLAS_Lumi"):
            ipc = True
    if dict_syst_check["ditau"]:
        if key.startswith("ATLAS_TAU") or key.startswith("ATLAS_DiTauSF"):
            ipc = True
    if dict_syst_check["jetmet"]:
        if key.startswith("ATLAS_FATJET") or key.startswith("ATLAS_MET_SoftTrk"):
            ipc = True
    if dict_syst_check["ftag"]:
        if key.startswith("ATLAS_FT_EFF"):
            ipc = True
    if dict_syst_check["bkg"]:
        if key.startswith("ATLAS_FF") or key.startswith("ATLAS_TTBAR") or key.startswith("ATLAS_ZhfSF"):
            ipc = True
    if dict_syst_check["sig"]:
        if key.startswith("ATLAS_SigAccUnc"):
            ipc = True

    return ipc


def common_setting(mass):
    from configManager import configMgr
    from ROOT import kBlack, kGray, kRed, kPink, kViolet, kBlue, kAzure, kGreen, \
        kOrange
    from configWriter import Sample
    from systematic import Systematic
    import os

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

    ##########################

    # Setting the parameters of the hypothesis test
    configMgr.doExclusion = True  # True=exclusion, False=discovery
    configMgr.nTOYs = 10000  # default=5000
    configMgr.calculatorType = 0  # 2=asymptotic calculator, 0=frequentist calculator
    configMgr.testStatType = 3  # 3=one-sided profile likelihood test statistic (LHC default)
    configMgr.nPoints = 30  # number of values scanned of signal-strength for upper-limit determination of signal strength.
    configMgr.writeXML = False

    # Pruning
    # - any overallSys systematic uncertainty if the difference of between the up variation and the nominal and between
    #   the down variation and the nominal is below a certain (user) given threshold
    # - for histoSys types, the situation is more complex:
    #   - a first check is done if the integral of the up histogram - the integral of the nominal histogram is smaller
    #     than the integral of the nominal histogram and the same for the down histogram
    #   - then a second check is done if the shape of the up, down and nominal histograms is very similar Only when both
    #     conditions are fulfilled the systematics will be removed.
    # default is False, so the pruning is normally not enabled
    configMgr.prun = True
    # The threshold to decide if an uncertainty is small or not is set by configMgr.prunThreshold = 0.005
    # where the number gives the fraction of deviation with respect to the nominal histogram below which an uncertainty
    # is considered to be small. The default is currently set to 0.01, corresponding to 1 % (This might be very aggressive
    # for the one or the other analyses!)
    configMgr.prunThreshold = 0.005
    # method 1: a chi2 test (this is still a bit experimental, so watch out if this is working or not)
    # method 2: checking for every bin of the histograms that the difference between up variation and nominal and down (default)
    configMgr.prunMethod = 2
    # variation and nominal is below a certain threshold.
    # Smoothing: HistFitter does not provide any smoothing tools.
    # More Details: https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/HistFitterAdvancedTutorial#Pruning_in_HistFitter

    ##########################

    # Keep SRs also in background fit confuguration
    configMgr.keepSignalRegionType = True
    configMgr.blindSR = BLIND
    # configMgr.useSignalInBlindedData = True

    # Give the analysis a name
    configMgr.analysisName = "bbtautau" + "X" + mass
    configMgr.histCacheFile = "data/" + configMgr.analysisName + ".root"
    configMgr.outputFileName = "results/" + configMgr.analysisName + "_Output.root"

    # Define cuts
    configMgr.cutsDict["SR"] = "1."

    # Define weights
    configMgr.weights = "1."

    # Define samples
    list_samples = []

    yields_mass = yields[mass]
    for process, yields_process in yields_mass.items():
        if process == 'data' or signal_prefix in process: continue
        # print("-> {} / Colour: {}".format(process, color_dict[process]))
        bkg = Sample(str(process), color_dict[process])
        bkg.setStatConfig(stat_config)
        # OLD: add lumi uncertainty (bkg/sig correlated, not for data-driven fakes)
        # NOW: add lumi by hand
        bkg.setNormByTheory(False)
        noms = yields_process["nEvents"]
        errors = yields_process["nEventsErr"] if use_mcstat else [0.0]
        # print("  nEvents (StatError): {} ({})".format(noms, errors))
        bkg.buildHisto(noms, "SR", my_disc, 0.5)
        bkg.buildStatErrors(errors, "SR", my_disc)
        if not stat_only and not no_syst:
            if process == 'fakes':
                key_here = "ATLAS_FF_1BTAG_SIDEBAND_Syst_hadhad"
                if not impact_check_continue(dict_syst_check, key_here):
                    bkg.addSystematic(
                        Systematic(key_here, configMgr.weights, 1.50, 0.50, "user", syst_type))
            else:
                key_here = "ATLAS_Lumi_Run2_hadhad"
                if not impact_check_continue(dict_syst_check, key_here):
                    bkg.addSystematic(
                        Systematic(key_here, configMgr.weights, 1.017, 0.983, "user", syst_type))
            for key, values in yields_process.items():
                if 'ATLAS' not in key: continue
                if impact_check_continue(dict_syst_check, key): continue;
                ups = values[0]
                downs = values[1]
                systUpRatio = [u / n if n != 0. else float(1.) for u, n in zip(ups, noms)]
                systDoRatio = [d / n if n != 0. else float(1.) for d, n in zip(downs, noms)]
                bkg.addSystematic(
                    Systematic(str(key), configMgr.weights, systUpRatio, systDoRatio, "user", syst_type))
        list_samples.append(bkg)

    # FIXME: This is unusual!
    top = Sample('top', kOrange)
    top.setStatConfig(False)  # No stat error
    top.setNormByTheory(False)  # consider lumi for it
    top.buildHisto([0.00001], "SR", my_disc, 0.5)  # small enough
    # HistFitter can accept such large up ratio
    # Systematic(name, weight, ratio_up, ratio_down, syst_type, syst_fistfactory_type)
    if not stat_only and not no_syst:
        key_here = 'ATLAS_TTBAR_YIELD_UPPER_hadhad'
        if not impact_check_continue(dict_syst_check, key_here):
            top.addSystematic(
                Systematic(key_here, configMgr.weights, unc_ttbar[mass], 0.9, "user", syst_type))
    list_samples.append(top)

    sigSample = Sample("Sig", kRed)
    sigSample.setNormFactor("mu_Sig", 1., 0., 100.)
    #sigSample.setStatConfig(stat_config)
    sigSample.setStatConfig(False)
    sigSample.setNormByTheory(False)
    noms = yields_mass[signal_prefix + mass]["nEvents"]
    errors = yields_mass[signal_prefix + mass]["nEventsErr"] if use_mcstat else [0.0]
    sigSample.buildHisto([noms[0]], "SR", my_disc, 0.5)
    #sigSample.buildStatErrors(errors, "SR", my_disc)
    for key, values in yields_mass[signal_prefix + mass].items():
        if 'ATLAS' not in key: continue
        if impact_check_continue(dict_syst_check, key):
            continue
        ups = values[0]
        downs = values[1]
        systUpRatio = [u / n if n != 0. else float(1.) for u, n in zip(ups, noms)]
        systDoRatio = [d / n if n != 0. else float(1.) for d, n in zip(downs, noms)]
        if not stat_only and not no_syst:
            sigSample.addSystematic(
                Systematic(str(key), configMgr.weights, systUpRatio, systDoRatio, "user", syst_type))
    if not stat_only and not no_syst:
        key_here = "ATLAS_SigAccUnc_hadhad"
        if not impact_check_continue(dict_syst_check, key_here):
            sigSample.addSystematic(
                Systematic(key_here, configMgr.weights, [1 + unc_sig_acc[mass] for i in range(my_nbins)],
                           [1 - unc_sig_acc[mass] for i in range(my_nbins)],
                           "user", syst_type))
        key_here = "ATLAS_Lumi_Run2_hadhad"
        if not impact_check_continue(dict_syst_check, key_here):
            sigSample.addSystematic(
                Systematic(key_here, configMgr.weights, 1.017, 0.983, "user", syst_type))

    list_samples.append(sigSample)

    # Set observed and expected number of events in counting experiment
    n_SPlusB = yields_mass[signal_prefix + mass]["nEvents"][0]+sum_of_bkg(yields_mass)[0]
    n_BOnly = sum_of_bkg(yields_mass)[0]
    if BLIND:
        ndata = sum_of_bkg(yields_mass)
    else:
        try:
            ndata = yields_mass["data"]["nEvents"]
        except:
            ndata = [0. for _ in range(my_nbins)]

    lumiError = 0.017  # Relative luminosity uncertainty

    dataSample = Sample("Data", kBlack)
    dataSample.setData()
    dataSample.buildHisto([n_BOnly], "SR", my_disc, 0.5)
    list_samples.append(dataSample)

    # Define top-level
    ana = configMgr.addFitConfig("SPlusB")
    ana.addSamples(list_samples)
    ana.setSignalSample(sigSample)

    # Define measurement
    meas = ana.addMeasurement(name="NormalMeasurement", lumi=1.0, lumiErr=lumiError / 100000.)
    # make it very small so that pruned
    # we use the one added by hand
    meas.addPOI("mu_Sig")
    #meas.statErrorType = "Poisson"
    # Fix the luminosity in HistFactory to constant
    meas.addParamSetting("Lumi", True, 1)

    # Add the channel
    chan = ana.addChannel(my_disc, ["SR"], my_nbins, my_xmin, my_xmax)
    chan.blind = BLIND
    #chan.statErrorType = "Poisson"
    ana.addSignalChannels([chan])

    # These lines are needed for the user analysis to run
    # Make sure file is re-made when executing HistFactory
    if configMgr.executeHistFactory:
        if os.path.isfile("data/%s.root" % configMgr.analysisName):
            os.remove("data/%s.root" % configMgr.analysisName)
