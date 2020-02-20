from __future__ import print_function
import pickle
from pprint import pprint
from sample_builder.sbsensitivities import SBSensitivities

from ROOT import gROOT

print("My ROOT version is {}".format(gROOT.GetVersion()))


def utest_sensitivities(debug):
    root_file_name = "../root_files/submitDir_v10_mc16ade.root"
    region_prefix = "2tag2pjet_0ptv_SRLRJwindow"
    masses = [1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000]
    binnings = {  # 'baseline': [0., 4000.],
        '0800': [0., 800., 4000.],
        '0900': [0., 900., 4000.],
        '1000': [0., 1000., 4000.],
        '1100': [0., 1100., 4000.],
        '1200': [0., 1200., 4000.],
        '1300': [0., 1300., 4000.],
        '1400': [0., 1400., 4000.],
        '1500': [0., 1500., 4000.], }
    # binnings = {#'baseline': [0., 4000.],
    #             '1000': [0., 1000., 4000.],
    #             '1100': [0., 1100., 4000.],
    #             '1200': [0., 1200., 4000.],
    #             '1300': [0., 1300., 4000.],
    #             '1400': [0., 1400., 4000.],
    #             '1500': [0., 1500., 4000.],
    #             '1600': [0., 1600., 4000.],
    #             '1700': [0., 1700., 4000.]}
    pickle_file_name = '../pickle_files/sensitivities.data'

    sbs = SBSensitivities(root_file_name, region_prefix, masses, binnings)

    sbs.signal_prefix = "Hhhbbtautau"
    sbs.cache_name = '../pickle_files/histograms.data'

    sbs.save_data(pickle_file_name)

    with open(pickle_file_name, 'rb') as sensitivities_pickle:
        sensitivities = pickle.load(sensitivities_pickle)

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    # x = np.array([1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700])
    x = np.array([800, 900, 1000, 1100, 1200, 1300, 1400, 1500])

    n_points = len(masses)
    y = [[] for _ in range(n_points)]
    for i in range(len(y)):
        for binstyle, _ in sorted(binnings.items(), key=lambda x: x[0]):
            y[i].append(sensitivities[binstyle][str(masses[i])])
        y[i] = np.array(y[i])
    if debug:
        print(y)

    # WARN: HC pandas DataFrame structure ...
    df = pd.DataFrame({'x': x, '1.0 TeV': y[0], '1.2 TeV': y[1],
                       '1.4 TeV': y[2], '1.6 TeV': y[3], '1.8 TeV': y[4],
                       '2.0 TeV': y[5], '2.5 TeV': y[6], '3.0 TeV': y[7], })

    # plt.style.use('fivethirtyeight')
    plt.style.use('seaborn-darkgrid')
    my_dpi = 96
    plt.figure(figsize=(960 / my_dpi, 960 / my_dpi), dpi=my_dpi)

    for column in df.drop('x', axis=1):
        plt.plot(df['x'], df[column], marker='', color='grey', linewidth=1, alpha=0.7)

    plt.plot(df['x'], df['1.6 TeV'], marker='', color='orange', linewidth=4, alpha=1.0)
    plt.plot(df['x'], df['1.8 TeV'], marker='', color='darkorange', linewidth=4, alpha=1.0)
    plt.plot(df['x'], df['2.0 TeV'], marker='', color='red', linewidth=4, alpha=1.0)
    plt.plot(df['x'], df['2.5 TeV'], marker='', color='lightcoral', linewidth=4, alpha=1.0)

    plt.xlim(700, 1600)
    # plt.xlim(900, 1800)

    num = 0
    for i in df.values[n_points - 1][1:]:
        num += 1
        name = list(df)[num]
        if name != '1.6 TeV' and name != '1.8 TeV' and name != '2.0 TeV' and name != '2.5 TeV':
            plt.text(1510, i, name, horizontalalignment='left', size='small', color='grey', fontsize=18)

    plt.text(1510, df['1.6 TeV'].tail(1), '1.6 TeV', horizontalalignment='left',
             size='small', color='orange', fontsize=20)
    plt.text(1510, df['1.8 TeV'].tail(1), '1.8 TeV', horizontalalignment='left',
             size='small', color='darkorange', fontsize=20)
    plt.text(1510, df['2.0 TeV'].tail(1), '2.0 TeV', horizontalalignment='left',
             size='small', color='red', fontsize=20)
    plt.text(1510, df['2.5 TeV'].tail(1), '2.5 TeV', horizontalalignment='left',
             size='small', color='lightcoral', fontsize=20)

    plt.title("Signal significance with respect to binning", loc='left', fontsize=22, fontweight=0, color='maroon')
    plt.xlabel("Boundary on visible HH mass", fontsize=22)
    plt.ylabel("Significance", fontsize=22)

    plt.show()

    if debug:
        pprint(sbs.data)


utest_sensitivities(False)
