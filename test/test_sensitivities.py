import sys

sys.path.insert(0, '/Users/bowen/PycharmProjects/SampleBuilderMaker/')
# from pprint import pprint
import pickle
from ROOT import gROOT

print(gROOT.GetVersion())
from sbmaker.sbsensitivities import SBSensitivities

filename = "/Users/bowen/Documents/work/Boosted/root_files/submitDir_v10_w23_mc16ade.root"
prefix = "2tag2pjet_0ptv_SRLRJM60160"
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

useCache = True

sbs = SBSensitivities(filename, prefix, binnings, None, useCache, True)

with open('/Users/bowen/PycharmProjects/SampleBuilderMaker/pickle_files/sensitivities.dictionary',
          'rb') as sensitivities_pickle:
    sensitivities = pickle.load(sensitivities_pickle)
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    # x = np.array([1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700])
    x = np.array([800, 900, 1000, 1100, 1200, 1300, 1400, 1500])
    mass = [1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000]
    y = [[], [], [], [], [], [], [], []]
    for i in range(len(y)):
        for binstyle, _ in sorted(binnings.items(), key=lambda x: x[0]):
            y[i].append(sensitivities[binstyle][str(mass[i])])
        y[i] = np.array(y[i])
    print(y)

    df = pd.DataFrame({'x': x, '1.0 TeV': y[0], '1.2 TeV': y[1],
                       '1.4 TeV': y[2], '1.6 TeV': y[3], '1.8 TeV': y[4],
                       '2.0 TeV': y[5], '2.5 TeV': y[6], '3.0 TeV': y[7], })

    # plt.style.use('fivethirtyeight')
    plt.style.use('seaborn-darkgrid')
    my_dpi = 96
    plt.figure(figsize=(960 / my_dpi, 960 / my_dpi), dpi=my_dpi)

    # multiple line plot
    for column in df.drop('x', axis=1):
        plt.plot(df['x'], df[column], marker='', color='grey', linewidth=1, alpha=0.7)

    # Now re do the interesting curve, but biger with distinct color
    plt.plot(df['x'], df['1.6 TeV'], marker='', color='orange', linewidth=4, alpha=1.0)
    plt.plot(df['x'], df['1.8 TeV'], marker='', color='darkorange', linewidth=4, alpha=1.0)
    plt.plot(df['x'], df['2.0 TeV'], marker='', color='red', linewidth=4, alpha=1.0)
    plt.plot(df['x'], df['2.5 TeV'], marker='', color='lightcoral', linewidth=4, alpha=1.0)

    # Change xlim
    plt.xlim(700, 1600)
    # plt.xlim(900, 1800)

    # Let's annotate the plot
    num = 0
    for i in df.values[7][1:]:
        num += 1
        name = list(df)[num]
        if name != '1.6 TeV' and name != '1.8 TeV' and name != '2.0 TeV' and name != '2.5 TeV':
            plt.text(1510, i, name, horizontalalignment='left', size='small', color='grey', fontsize=18)

    # And add a special annotation for the group we are interested in
    plt.text(1510, df['1.6 TeV'].tail(1), '1.6 TeV', horizontalalignment='left', size='small', color='orange',
             fontsize=20)
    plt.text(1510, df['1.8 TeV'].tail(1), '1.8 TeV', horizontalalignment='left', size='small', color='darkorange',
             fontsize=20)
    plt.text(1510, df['2.0 TeV'].tail(1), '2.0 TeV', horizontalalignment='left', size='small', color='red', fontsize=20)
    plt.text(1510, df['2.5 TeV'].tail(1), '2.5 TeV', horizontalalignment='left', size='small', color='lightcoral',
             fontsize=20)

    # Add titles
    plt.title("Signal significance with respect to binning", loc='left', fontsize=22, fontweight=0, color='maroon')
    plt.xlabel("Boundary on visible HH mass", fontsize=22)
    plt.ylabel("Significance", fontsize=22)

    plt.show()

# pprint(sbs.sensitivities)

## EOF
