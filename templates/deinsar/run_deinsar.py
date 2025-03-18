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
datadir = "**di_data_directories**"
os.chdir(os.path.dirname(os.path.realpath(__file__)))
processdir = os.path.abspath("process")

master = "**master**"
startdate = "**startdate**"
stopdate = "**enddate**"
sensor = "**sensor**"  # ERS, ERSENV, ENV, TSX, TDX, PAZ, RSAT2, Cosmo, ALOS2
polarisations = eval("**polarisation**")

polarisations = [f"_{pol}" for pol in polarisations]
if "_HH" in polarisations:
    polarisations[polarisations.index("_HH")] = ""

do_orbit = "**di_do_orbit**"
do_crop = "**di_do_crop**"
do_tsx_deramp = "**di_do_tsx_deramp**"
do_simamp = "**di_do_simamp**"
do_mtiming = "**di_do_mtiming**"
do_ovs = "**di_do_ovs**"
do_choose_master = "**di_do_choose_master**"
do_coarseorb = "**di_do_coarseorb**"
do_coarsecorr = "**di_do_coarsecorr**"
do_finecoreg = "**di_do_finecoreg**"
do_reltiming = "**di_do_reltiming**"
do_dembased = "**di_do_dembased**"
do_coregpm = "**di_do_coregpm**"
do_comprefpha = "**di_do_comprefpha**"
do_comprefdem = "**di_do_comprefdem**"
do_resample = "**di_do_resample**"
do_tsx_reramp = "**di_do_tsx_reramp**"
do_interferogram = "**di_do_interferogram**"
do_subtrrefpha = "**di_do_subtrrefpha**"
do_subtrrefdem = "**di_do_subtrrefdem**"
do_coherence = "**di_do_coherence**"
do_geocoding = "**di_do_geocoding**"

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
        print(f"Warning: orbit requested but sensor is {sensor} (should be ENV, ERS or RSAT2). Skipping...")

if do_crop == "1":
    for pol in polarisations:
        crop(slcs, processdir, altimg=pol)

if do_tsx_deramp == "1":
    if sensor != "TSX":
        print(f"Warning: TSX deramp requested but sensor is {sensor}. Skipping...")
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
        print(f"Warning: TSX reramp requested but sensor is {sensor}. Skipping...")
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
        print(f"Warning: TSX reramp requested but sensor is {sensor}. Skipping...")
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
