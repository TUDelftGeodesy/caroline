# DORIS stack processing
#
# Needs deinsar in pythonpath, and precise orbits in SAR_ODR_DIR if orbit() is called.
# Add the following lines to your .bashrc file:
# export PYTHONPATH=$PYTHONPATH:/home/everybody/software/deinsar
# export SAR_ODR_DIR=/home/everybody/orbits/
#
# or add a local copy
#
# Edit input.comprefdem to contain the correct DEM after step copy_inputfiles()
#
# SVD: This file has been set up specifically to work with CAROLINE, which will fill in the
# star-marked parameters. To run standalone, please replace all variables where appropriate


import os

from deinsar import (
    choose_master,
    coarsecorr,
    coarseorb,
    coherence,
    comprefdem,
    comprefpha,
    coregpm,
    crop,
    dembased,
    deramp_TSX,
    fake_slant2h,
    finecoreg,
    geocoding,
    interferogram,
    link_files,
    mtiming,
    orbit_ENV,
    orbit_ERS,
    orbit_RSAT2,
    ovs,
    readfiles,
    reltiming,
    reramp_TSX,
    resample,
    simamp,
    subtrrefdem,
    subtrrefpha,
)

# Parameters
datadir = "**deinsar:input:data-directories**"
os.chdir(os.path.dirname(os.path.realpath(__file__)))
processdir = os.path.abspath("process")

master = "**master**"
startdate = "**startdate**"
stopdate = "**enddate**"
sensor = "**general:input-data:sensor**"  # ERS, ERSENV, ENV, TSX, TDX, PAZ, RSAT2, Cosmo, ALOS2
polarisations = eval("**general:input-data:polarisation**")

# Note: this file is run in Python 2.7, in which f strings do not exist (so f"_{pol}" does not work)
polarisations = ["_" + pol for pol in polarisations]
if "_HH" in polarisations:
    polarisations[polarisations.index("_HH")] = ""

do_orbit = "**deinsar:deinsar-settings:do-orbit**"
do_crop = "**deinsar:deinsar-settings:do-crop**"
do_tsx_deramp = "**deinsar:deinsar-settings:do-tsx-deramp**"
do_simamp = "**deinsar:deinsar-settings:do-simamp**"
do_mtiming = "**deinsar:deinsar-settings:do-mtiming**"
do_ovs = "**deinsar:deinsar-settings:do-ovs**"
do_choose_master = "**deinsar:deinsar-settings:do-choose-master**"
do_coarseorb = "**deinsar:deinsar-settings:do-coarseorb**"
do_coarsecorr = "**deinsar:deinsar-settings:do-coarsecorr**"
do_finecoreg = "**deinsar:deinsar-settings:finecoreg:do-finecoreg**"
do_reltiming = "**deinsar:deinsar-settings:do-reltiming**"
do_dembased = "**deinsar:deinsar-settings:do-dembased**"
do_coregpm = "**deinsar:deinsar-settings:do-coregpm**"
do_comprefpha = "**deinsar:deinsar-settings:do-comprefpha**"
do_comprefdem = "**deinsar:deinsar-settings:do-comprefdem**"
do_resample = "**deinsar:deinsar-settings:do-resample**"
do_tsx_reramp = "**deinsar:deinsar-settings:do-tsx-reramp**"
do_interferogram = "**deinsar:deinsar-settings:do-interferogram**"
do_subtrrefpha = "**deinsar:deinsar-settings:do-subtrrefpha**"
do_subtrrefdem = "**deinsar:deinsar-settings:do-subtrrefdem**"
do_coherence = "**deinsar:deinsar-settings:do-coherence**"
do_geocoding = "**deinsar:deinsar-settings:do-geocoding**"

# Processing steps
link_files(datadir, processdir, sensor)

slcs = [f for f in os.listdir(processdir) if len(f) == 8 and f[0] in "12"]
slcs.sort()

if startdate.isspace():
    idx1 = 0
else:
    idx1 = slcs.index(startdate)

if stopdate.isspace():
    idx2 = len(slcs)
else:
    idx2 = slcs.index(stopdate) + 1  # SVD: +1 so stopdate is included

slcs = slcs[idx1:idx2]

readfiles(slcs, processdir)

if do_orbit == "1":
    if sensor == "ENV":
        orbit_ENV(slcs, processdir)
    elif sensor == "ERS":
        orbit_ERS(slcs, processdir)
    elif sensor == "RSAT2":
        orbit_RSAT2(slcs, processdir)
    else:
        print("Warning: orbit requested but sensor is " + sensor + " (should be ENV, ERS or RSAT2). Skipping...")

if do_crop == "1":
    for pol in polarisations:
        crop(slcs, processdir, altimg=pol)

if do_tsx_deramp == "1":
    if sensor != "TSX":
        print("Warning: TSX deramp requested but sensor is " + sensor + ". Skipping...")
    else:
        for pol in polarisations:
            deramp_TSX(slcs, processdir, altimg=pol)

if do_simamp == "1":
    simamp(master, processdir)

if do_mtiming == "1":
    mtiming(master, processdir)

if do_ovs == "1":
    for pol in polarisations:
        ovs(slcs, processdir, altimg=pol)

if do_choose_master == "1":
    for pol in polarisations:
        choose_master(master, processdir, altimg=pol)

if do_coarseorb == "1":
    coarseorb(slcs, processdir)

if do_coarsecorr == "1":
    coarsecorr(slcs, processdir)

if do_finecoreg == "1":
    finecoreg(slcs, processdir)

if do_reltiming == "1":
    reltiming(slcs, processdir)

if do_dembased == "1":
    dembased(slcs, processdir)

if do_coregpm == "1":
    coregpm(slcs, processdir)

# first do only the first polarization
if do_resample == "1":
    resample(slcs, processdir, altimg=polarisations[0])

if do_tsx_reramp == "1":
    if sensor != "TSX":
        print("Warning: TSX reramp requested but sensor is " + sensor + ". Skipping...")
    else:
        reramp_TSX(slcs, master, processdir, altimg=polarisations[0])

# compute flat earth and dem reference phase only once for all polarizations
if do_comprefpha == "1":
    comprefpha(slcs, processdir)

if do_comprefdem == "1":
    comprefdem(slcs, processdir)

# from here all steps are performed per polarization
# this resample step should be located here, since the ifgs.res files is copied with the coregistration and
# reference phase parameters, but without the interferograms
if do_resample == "1":
    for pol in polarisations[1:]:
        resample(slcs, processdir, altimg=pol)

if do_tsx_reramp == "1":
    if sensor != "TSX":
        print("Warning: TSX reramp requested but sensor is " + sensor + ". Skipping...")
    else:
        for pol in polarisations[1:]:
            reramp_TSX(slcs, master, processdir, altimg=pol)

if do_interferogram == "1":
    for pol in polarisations:
        interferogram(slcs, processdir, altimg=pol)

if do_subtrrefpha == "1":
    for pol in polarisations:
        subtrrefpha(slcs, processdir, altimg=pol)

if do_subtrrefdem == "1":
    for pol in polarisations:
        subtrrefdem(slcs, processdir, altimg=pol)

if do_coherence == "1":
    for pol in polarisations:
        coherence(slcs, processdir, altimg=pol)

if do_geocoding == "1":
    fake_slant2h(master, processdir)
    geocoding(master, processdir)
