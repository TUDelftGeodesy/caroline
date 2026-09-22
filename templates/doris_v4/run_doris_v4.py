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
datadir = "**doris_v4:input:data-directories**"
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

do_orbit = "**doris_v4:doris_v4-settings:do-orbit**"
do_crop = "**doris_v4:doris_v4-settings:do-crop**"
do_tsx_deramp = "**doris_v4:doris_v4-settings:do-tsx-deramp**"
do_simamp = "**doris_v4:doris_v4-settings:do-simamp**"
do_mtiming = "**doris_v4:doris_v4-settings:do-mtiming**"
do_ovs = "**doris_v4:doris_v4-settings:do-ovs**"
do_choose_master = "**doris_v4:doris_v4-settings:do-choose-master**"
do_coarseorb = "**doris_v4:doris_v4-settings:do-coarseorb**"
do_coarsecorr = "**doris_v4:doris_v4-settings:do-coarsecorr**"
do_finecoreg = "**doris_v4:doris_v4-settings:finecoreg:do-finecoreg**"
do_reltiming = "**doris_v4:doris_v4-settings:do-reltiming**"
do_dembased = "**doris_v4:doris_v4-settings:do-dembased**"
do_coregpm = "**doris_v4:doris_v4-settings:do-coregpm**"
do_comprefpha = "**doris_v4:doris_v4-settings:do-comprefpha**"
do_comprefdem = "**doris_v4:doris_v4-settings:do-comprefdem**"
do_resample = "**doris_v4:doris_v4-settings:do-resample**"
do_tsx_reramp = "**doris_v4:doris_v4-settings:do-tsx-reramp**"
do_interferogram = "**doris_v4:doris_v4-settings:do-interferogram**"
do_subtrrefpha = "**doris_v4:doris_v4-settings:do-subtrrefpha**"
do_subtrrefdem = "**doris_v4:doris_v4-settings:do-subtrrefdem**"
do_coherence = "**doris_v4:doris_v4-settings:do-coherence**"
do_geocoding = "**doris_v4:doris_v4-settings:do-geocoding**"

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
