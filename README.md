# This repo: `SampleBuilder`

Contact: bowen.zhang@cern.ch

## Introduction
This small tool read information from a `CxAODReader_HH_bbtautau` boosted analysis output histogram file (merged by [`bohadd`](https://gitlab.cern.ch/zhangb/BOhadd)) and write them to a pickle data file. Keeping all the nominal and variational yields. Later this file will be loaded by the configuration file of [`HistFitter`](https://gitlab.cern.ch/HistFitter/HistFitter).

## Main function

To create the pickle data file, one can use the `build_data.py` in `SampleBuilder/`

```
./build_data -i root_files/submitDir_v10_mc16ade.root --histograms pickle_files/histograms.data --yields pickle_files/yields.data
```
or just

```
./build_data
```
the arguments are filled by default.

## Other functions

- Print yield table.
- Print systematic impact (on background yields) table.
- Make comparison plot for sensitivity study (using different binnings)
- ...

See the test scripts in `test/` for details. Step by step run:

```
python utest_histograms.py
python utest_yields.py
python utest_sensitivities.py
python utest.py
```
> **NOTE:** This was used for testing the classes, so please take care of the hardcoded pathes.


# How to run the statistical analysis step by step (Important)

## Step 1: setup `HistFitter` and `SampleBuilder`
### Create a new folder:
```
mkdir MyBoostedStatAna && cd $_
```
### Create a `setup.sh`:
```
#!/usr/bin/env bash
HISTFITTER_COMMITID=6caa1a7de5a2a878308be48481873805bcca23d8

# Setup ATLAS
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh --quiet

# Setup ROOT
if [ -x "$(command -v showVersions)" ]
then
    export RECOMMENDEDROOTVERSION=$( showVersions root | grep recommended | awk '{print $2}' )
else
    export RECOMMENDEDROOTVERSION=6.14.04-x86_64-slc6-gcc62-opt
fi
export ALRB_rootVersion=6.14.04-x86_64-slc6-gcc62-opt
lsetup "root $RECOMMENDEDROOTVERSION"

# Setup HistFitter
if [ ! -d HistFitter ]; then
    git clone ssh://git@gitlab.cern.ch:7999/HistFitter/HistFitter.git
    cd HistFitter
    git checkout ${HISTFITTER_COMMITID}
    cd src && make
    cd ../..
fi
cd HistFitter && source setup.sh && cd ..

# Setup SampleBuilder
if [ ! -d SampleBuilder ]; then
    git clone ssh://git@gitlab.cern.ch:7999/zhangb/SampleBuilder.git
fi
cd SampleBuilder
export SAMPLEBUILDER=${PWD}
export PYTHONPATH=${PWD}:$PYTHONPATH
echo "set \$SAMPLEBUILDER=${SAMPLEBUILDER} and add it to \$PYTHONPATH"
cd ..

```
> **NOTE:** 
> The versions used until 26/12/2019
> 
> - `HistFitter`: commit id = `6caa1a7de5a2a878308be48481873805bcca23d8`
> - `SampleBuilder`: master branch
> - `ROOT`: `6.14.04-x86_64-slc6-gcc62-opt`
> 

### Run it under `MyBoostedStatAna`
```
source setup.sh
```
After setting up ATLAS environment and `ROOT`, it will check out the `HistFitter` with a specific commit ID (ensuring reproducibility) and compile the C++ source code. Then check out the `SampleBuilder`.

### On every login
```
source setup.sh
```
If `HistFitter` and `SampleBuilder` are already existed. This will only setup the required environments.

## Step 2: Create the pickle data
This step writes the pickle file. Here is my example script `build_data.sh`:

```
####################################
# Usage:			   #
# source build_data.sh [root_file] #
# 				   #
# root_file:			   #
# merged by `bohadd`		   #
####################################

MYROOTFILE=$( readlink -f $1 )

pushd SampleBuilder
if [ $# -eq 0 ]; then
    echo "Make sure root_files/submitDir_v10_mc16ade.root does exist"
else
    echo "Linking ${MYROOTFILE} to root_files/submitDir_v10_mc16ade.root"
    ln -nfs ${MYROOTFILE} root_files/submitDir_v10_mc16ade.root
fi
./build_data
popd

```

Run this under the `MyBoostedStatAna` that we created just now with the path to your root file: 

```
source build_data.sh /path/to/my/root/file/cxaod_output.root
```

## Step 3: Run HistFitter with the pickle data and the configure files
This step runs the actual statistical analysis with `HistFitter`. Here is my example script `fit_hist.sh`:

```
################################
# Usage:       #
# source fit_hist.sh [job_id]  #
#        #
# job_id:       #
# Any name to identify the job #
################################
MYJOBID=$1
if [ -z ${MYJOBID} ]; then
    MYJOBID=`date '+%Y%m%d_%H-%M-%S'`
fi
mkdir run_${MYJOBID} && cd $_

if [ -z ${SAMPLEBUILDER} ]; then
    cp ../SampleBuilder/pickle_files/* .
    cp ../SampleBuilder/forHistFitter/* .
else
    cp ${SAMPLEBUILDER}/pickle_files/* .
    cp ${SAMPLEBUILDER}/forHistFitter/* .
fi

# # run on local machine
# MASSPOINT="X1100"
# mkdir ${MASSPOINT} && cd $_
# cp ../config_common.py ../config_${MASSPOINT}.py ../yields.dictionary .
# HistFitter.py -F excl -w -f -l -D "before,after,corrMatrix,likelihood,systematics" config_${MASSPOINT}.py

# run on ihep batch system
MYBATCHSCRIPT=batchjob_${MYJOBID}.sh
touch ${MYBATCHSCRIPT}
chmod a+x ${MYBATCHSCRIPT}
cat <<EOF > ${MYBATCHSCRIPT}
#!/bin/bash
cd ${PWD}/../ && source setup.sh
cd ${PWD}
MASSPOINT=\$1
mkdir \${MASSPOINT} && cd \$_
cp ../config_common.py ../config_\${MASSPOINT}.py ../yields.dictionary .
HistFitter.py -F excl -w -f -l -D "before,after,corrMatrix,likelihood,systematics" config_\${MASSPOINT}.py
EOF

for mass in X1000 X1100 X1200 X1400 X1600 X1800 X2000 X2500 X3000
do
    hep_sub ${PWD}/${MYBATCHSCRIPT} -g atlas -o batchjob_${MYJOBID}_${mass}.out -e batchjob_${MYJOBID}_${mass}.err -np 2 -mem 3000 -argu ${mass}
done

# # run on lxplus HTCondor
# MYHTCONDORSCRIPT=htcondor_${MYJOBID}.sh
# touch ${MYHTCONDORSCRIPT}
# chmod a+x ${MYHTCONDORSCRIPT}
# cat <<EOF > ${MYHTCONDORSCRIPT}
# #!/bin/bash
# cd ${PWD}/../ && source setup.sh
# cd ${PWD}
# MASSPOINT=\$1
# mkdir \${MASSPOINT} && cd \$_
# cp ../config_common.py ../config_\${MASSPOINT}.py ../yields.dictionary .
# HistFitter.py -F excl -w -f -l -D "before,after,corrMatrix,likelihood,systematics" config_\${MASSPOINT}.py

# EOF

# MYHTCONDORSUBMIT=htcondor_${MYJOBID}.sub
# touch ${MYHTCONDORSUBMIT}
# cat <<EOF > ${MYHTCONDORSUBMIT}
# executable            = htcondor_${MYJOBID}.sh
# output                = htcondor_${MYJOBID}.\$(ClusterId).\$(ProcId).out
# error                 = htcondor_${MYJOBID}.\$(ClusterId).\$(ProcId).err
# log                   = htcondor_${MYJOBID}.\$(ClusterId).\$(ProcId).log
# request_cpus          = 2
# +JobFlavour           = "tomorrow"
# queue arguments from arguments.txt

# EOF

# MYARGUMENTS=arguments.txt
# touch ${MYARGUMENTS}
# cat <<EOF > ${MYARGUMENTS}
# X1000
# X1100
# X1200
# X1400
# X1600
# X1800
# X2000
# X2500
# X3000
# EOF

# condor_submit ${MYHTCONDORSUBMIT}

```
Run this under the `MyBoostedStatAna` that we created just now with a job ID (If it's empty, it will use the date and time as job ID by default): 

```
source fit_hist.sh v1-unblind
```
**TODO:**

- run on taurus

# Reference
HistFitter TWiki: [Basic](https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/HistFitterTutorial) | [Advanced](https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/HistFitterAdvancedTutorial) | [Paper](https://arxiv.org/pdf/1410.1280.pdf)
