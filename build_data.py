# !/usr/bin/env python
# encoding: utf-8
"""
main.py
~~~~~~~~~

Main function to get yield data from Reader output

"""

# IMPORT
from __future__ import print_function

import argparse

from pprint import pprint
from sample_builder.sbhistograms import SBHistograms
from utils.logging_tools import get_logger

from ROOT import gROOT

print("My ROOT version is {}".format(gROOT.GetVersion()))


def main(args):
    logger = get_logger("MAIN", args.msglvl)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", default="",
                        help="Name of merged file.")
    parser.add_argument("-i", "--input", default="", nargs='*',
                        help="Input root file pattern, Same as those in hadd.")
    parser.add_argument("-l", "--msglvl", default="INFO",
                        help="Log message level.")
    parser.add_argument("-j", "--ncpus", default=10,
                        help="Number of parallel processes of hadd merge")

    args = parser.parse_args()

    main(args)
