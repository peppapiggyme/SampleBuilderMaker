import pickle
import copy

yields = None
with open('/scratch/ws/bozh923b-dihiggs/HistFitter/bbtautau/yields.dictionary', 'rb') as yields_pickle:
    yields = pickle.load(yields_pickle)

# my configuration
my_disc = "effmHH"  # discriminant variable (if set to "cuts", will force to use one bin!)
signal_prefix = "Hhhbbtautau"
stat_only = False
my_nbins = 2
my_xmin = 0.5
my_xmax = my_xmin + my_nbins

# shape_systs = ['SysFATJET_Medium_JET_Comb_Baseline_Kin',
#                'SysFATJET_Medium_JET_Comb_TotalStat_Kin',
#                'SysFATJET_Medium_JET_Comb_Modelling_Kin',
#                'SysFATJET_Medium_JET_Comb_Tracking_Kin',
#                'SysFATJET_JER', 'SysFATJET_JMR',
#                'SysTAUS_TRUEHADDITAU_EFF_JETID_TOTAL',
#                'SysTAUS_TRUEHADDITAU_SME_TES_TOTAL',
#                'SysMET_SoftTrk_ResoPerp', 'SysMET_SoftTrk_ResoPara',
#                'SysMET_JetTrk_Scale', 'SysMET_SoftTrk_Scale', ]


def sum_of_bkg(yields_mass):
    sum = [0. for _ in yields_mass["data"]["nEvents"]]
    for process, yields_process in yields_mass.items():
        if process != "data" and signal_prefix not in process:
            old_values = copy.deepcopy(sum)
            sum = [o + v for o, v in zip(old_values, yields_process["nEvents"])]
            del old_values
    return sum


def common_setting(mass):
    from configManager import configMgr
    from ROOT import kBlack, kWhite, kGray, kRed, kPink, kMagenta, kViolet, kBlue, kAzure, kCyan, kTeal, kGreen, \
        kSpring, kYellow, kOrange
    from configWriter import fitConfig, Measurement, Channel, Sample
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
    configMgr.nTOYs = 5000  # default=5000
    configMgr.calculatorType = 0  # 2=asymptotic calculator, 0=frequentist calculator
    configMgr.testStatType = 3  # 3=one-sided profile likelihood test statistic (LHC default)
    configMgr.nPoints = 20  # number of values scanned of signal-strength for upper-limit determination of signal strength.
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
    # configMgr.blindSR = True
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
        bkg.setStatConfig(True)
        # add lumi uncertainty (bkg/sig correlated, not for data-driven fakes)
        if process == 'fakes':
            bkg.setNormByTheory(False)
        else:
            bkg.setNormByTheory(True)
        noms = yields_process["nEvents"]
        errors = yields_process["nEventsErr"]
        # print("  nEvents (StatError): {} ({})".format(noms, errors))
        bkg.buildHisto(noms, "SR", my_disc, 0.5)
        bkg.buildStatErrors(errors, "SR", my_disc)
        if not stat_only:
            for key, values in yields_process.items():
                if 'Sys' not in key: continue
                ups = values[0]
                downs = values[1]
                systUpRatio = [u / n if n != 0. else float(1.) for u, n in zip(ups, noms)]
                systDoRatio = [d / n if n != 0. else float(1.) for d, n in zip(downs, noms)]
                bkg.addSystematic(Systematic(str(key), configMgr.weights, systUpRatio, systDoRatio, "user", "overallNormHistoSys"))
        list_samples.append(bkg)

    sigSample = Sample("Sig", kRed)
    sigSample.setNormFactor("mu_Sig", 1., 0., 100.)
    sigSample.setStatConfig(True)
    sigSample.setNormByTheory(True)
    noms = yields_mass[signal_prefix + mass]["nEvents"]
    errors = yields_mass[signal_prefix + mass]["nEventsErr"]
    sigSample.buildHisto(noms, "SR", my_disc, 0.5)
    sigSample.buildStatErrors(errors, "SR", my_disc)
    for key, values in yields_mass[signal_prefix + mass].items():
        if 'Sys' not in key: continue
        ups = values[0]
        downs = values[1]
        systUpRatio = [u / n if n != 0. else float(1.) for u, n in zip(ups, noms)]
        systDoRatio = [d / n if n != 0. else float(1.) for d, n in zip(downs, noms)]
        sigSample.addSystematic(Systematic(str(key), configMgr.weights, systUpRatio, systDoRatio, "user", "overallNormHistoSys"))
    list_samples.append(sigSample)

    # Set observed and expected number of events in counting experiment
    ndata = sum_of_bkg(yields_mass)
    lumiError = 0.017  # Relative luminosity uncertainty

    dataSample = Sample("Data", kBlack)
    dataSample.setData()
    dataSample.buildHisto(ndata, "SR", my_disc, 0.5)

    list_samples.append(dataSample)

    # Define top-level
    ana = configMgr.addFitConfig("SPlusB")
    ana.addSamples(list_samples)
    ana.setSignalSample(sigSample)

    # Define measurement
    meas = ana.addMeasurement(name="NormalMeasurement", lumi=1.0, lumiErr=lumiError)
    meas.addPOI("mu_Sig")
    # meas.addParamSetting("Lumi",True,1)

    # Add the channel
    chan = ana.addChannel(my_disc, ["SR"], my_nbins, my_xmin, my_xmax)
    # chan.blind = True
    ana.addSignalChannels([chan])

    # These lines are needed for the user analysis to run
    # Make sure file is re-made when executing HistFactory
    if configMgr.executeHistFactory:
        if os.path.isfile("data/%s.root" % configMgr.analysisName):
            os.remove("data/%s.root" % configMgr.analysisName)