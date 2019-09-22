import pickle
yields = None
with open('/scratch/ws/bozh923b-dihiggs/HistFitter/bbtautau/yields.dictionary', 'rb') as yields_pickle:
    yields = pickle.load(yields_pickle)


def sum_of_bkg(yields_mass):
    sum = 0
    for process, yields_process in yields_mass.items():
        if process != "data" and "Hhhbbtautau" not in process:
            sum += yields_process["nEvents"]
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
                  "ttbar": kOrange, "stop": kOrange, "ZZPw": kGray,
                  "WZPw": kGray, "WWPw": kGray, "fakes": kPink,
                  "Hhhbbtautau1000": kRed, "Hhhbbtautau1200": kRed,
                  "Hhhbbtautau1400": kRed, "Hhhbbtautau1600": kRed,
                  "Hhhbbtautau1800": kRed, "Hhhbbtautau2000": kRed,
                  "Hhhbbtautau2500": kRed, "Hhhbbtautau3000": kRed,
                  }

    ##########################

    # Setting the parameters of the hypothesis test
    configMgr.doExclusion=True # True=exclusion, False=discovery
    configMgr.nTOYs=5000      # default=5000
    configMgr.calculatorType=0 # 2=asymptotic calculator, 0=frequentist calculator
    configMgr.testStatType=3   # 3=one-sided profile likelihood test statistic (LHC default)
    configMgr.nPoints=20       # number of values scanned of signal-strength for upper-limit determination of signal strength.
    #configMgr.seed=41
    #configMgr.toySeed=43

    configMgr.writeXML = False

    ##########################

    # Keep SRs also in background fit confuguration
    configMgr.keepSignalRegionType = True
    #configMgr.blindSR = True
    #configMgr.useSignalInBlindedData = True

    # Give the analysis a name
    configMgr.analysisName = "bbtautau"+"X"+mass
    configMgr.outputFileName = "results/%s_Output.root"%configMgr.analysisName

    # Define cuts
    configMgr.cutsDict["SR"] = "1."

    # Define weights
    configMgr.weights = "1."

    # Define samples
    list_samples = []

    yields_mass = yields[mass]
    for process, yields_process in yields_mass.items():
        if process == 'data' or "Hhhbbtautau" in process: continue
        print("-> {} / Colour: {}".format(process, color_dict[process]))
        bkg = Sample(str(process), color_dict[process])
        bkg.setStatConfig(True)
        # add lumi uncertainty (bkg/sig correlated, not for data-driven fakes)
        if process == 'fakes': 
            bkg.setNormByTheory(False)
        else: 
            bkg.setNormByTheory(True)
        nominal = yields_process["nEvents"]
        staterror = yields_process["nEventsErr"]
        print("  nEvents (StatError): {} ({})".format(nominal, staterror))
        bkg.buildHisto([nominal], "SR", "cuts", 0.5)
        bkg.buildStatErrors([staterror], "SR", "cuts")
        for key, value in yields_process.items():
            if 'Sys' not in key: continue
            systUpRatio = value[0] / nominal
            systDoRatio = value[1] / nominal
            bkg.addSystematic(Systematic(str(key), configMgr.weights, systUpRatio, systDoRatio, "user", "userOverallSys"))
        list_samples.append(bkg)

    sigSample = Sample("Sig",kRed)
    sigSample.setNormFactor("mu_Sig",1.,0.,100.)
    sigSample.setStatConfig(True)
    sigSample.setNormByTheory(True)
    sigSample.buildHisto([yields_mass["Hhhbbtautau"+mass]["nEvents"]],"SR","cuts",0.5)
    sigSample.buildStatErrors([yields_mass["Hhhbbtautau"+mass]["nEventsErr"]],"SR","cuts")
    for key, value in yields_mass["Hhhbbtautau"+mass].items():
        if 'Sys' not in key: continue
        systUpRatio = value[0] / yields_mass["Hhhbbtautau"+mass]["nEvents"]
        systDoRatio = value[1] / yields_mass["Hhhbbtautau"+mass]["nEvents"]
        sigSample.addSystematic(Systematic(str(key), configMgr.weights, systUpRatio, systDoRatio, "user", "userOverallSys"))
    list_samples.append(sigSample)

    # Set observed and expected number of events in counting experiment
    ndata     =  sum_of_bkg(yields_mass)
    lumiError =  0.017 	# Relative luminosity uncertainty

    dataSample = Sample("Data",kBlack)
    dataSample.setData()
    dataSample.buildHisto([ndata],"SR","cuts",0.5)

    list_samples.append(dataSample)

    # Define top-level
    ana = configMgr.addFitConfig("SPlusB")
    ana.addSamples(list_samples)
    ana.setSignalSample(sigSample)

    # Define measurement
    meas = ana.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=lumiError)
    meas.addPOI("mu_Sig")
    #meas.addParamSetting("Lumi",True,1)

    # Add the channel
    chan = ana.addChannel("cuts",["SR"],1,0.5,1.5)
    #chan.blind = True
    ana.addSignalChannels([chan])

    # These lines are needed for the user analysis to run
    # Make sure file is re-made when executing HistFactory
    if configMgr.executeHistFactory:
        if os.path.isfile("data/%s.root" % configMgr.analysisName):
            os.remove("data/%s.root" % configMgr.analysisName)
