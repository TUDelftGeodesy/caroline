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
# curly brackets. It cannot be run standalone.


import os
from deinsar import *

## Parameters
datadir = '{datadir}'
os.chdir(os.path.dirname(os.path.realpath(__file__)))
processdir = os.path.abspath('process')

master = '{master}'
startdate = '{startdate}'
stopdate = '{stopdate}'
sensor = '{sensor}'  # ERS, ERSENV, ENV, TSX, TDX, PAZ, RSAT2, Cosmo, ALOS2

## Processing steps
link_files(datadir, processdir, sensor)

# this is already done by generat_deinsar_input_files
# copy_inputfiles(sensor, processdir)
## After this step, adopt the local input files with your processing settings
# os._exit(1)

slcs = [f for f in os.listdir(processdir) if len(f) == 8 and f[0:2] == '19' or f[0:2] == '20']
slcs.sort()

#if not startdate:
if startdate.isspace():
   idx1 = 0
else:
   idx1 = slcs.index(startdate)
#   print(idx1)
#   if idx1==-1:
#      return 'Error, [startdate] not in slc list.'

#if not stopdate:
if stopdate.isspace():
   idx2 = len(slcs)
else:
   idx2 = slcs.index(stopdate) + 1  # SVD: +1 so stopdate is included
#   print(idx2)
#   if idx2==-1:
#      return 'Error, [stopdate] not in slc list.'

slcs = slcs[idx1:idx2]


readfiles(slcs, processdir)

{do_orbit}orbit_{sensor}(slcs, processdir)

#plot_baselines(baselines(slcs, processdir))
#os._exit(1)

{do_crop_hh}crop(slcs, processdir)
{do_crop_hv}crop(slcs, processdir, altimg='_HV')
{do_crop_vh}crop(slcs, processdir, altimg='_VH')
{do_crop_vv}crop(slcs, processdir, altimg='_VV')

{do_tsx_deramp_hh}deramp_TSX(slcs, processdir)
{do_tsx_deramp_hv}deramp_TSX(slcs, processdir, altimg='_HV')
{do_tsx_deramp_vh}deramp_TSX(slcs, processdir, altimg='_VH')
{do_tsx_deramp_vv}deramp_TSX(slcs, processdir, altimg='_VV')

{do_simamp}simamp(master, processdir)

{do_mtiming}mtiming(master, processdir)

{do_ovs_hh}ovs(slcs, processdir)
{do_ovs_hv}ovs(slcs, processdir, altimg='_HV')
{do_ovs_vh}ovs(slcs, processdir, altimg='_VH')
{do_ovs_vv}ovs(slcs, processdir, altimg='_VV')

{do_choose_master_hh}choose_master(master, processdir)
{do_choose_master_hv}choose_master(master, processdir, altimg='_HV')
{do_choose_master_vh}choose_master(master, processdir, altimg='_VH')
{do_choose_master_vv}choose_master(master, processdir, altimg='_VV')
#os._exit(1)

{do_coarseorb}coarseorb(slcs, processdir)
{do_coarsecorr}coarsecorr(slcs, processdir)
{do_finecoreg}finecoreg(slcs, processdir)

{do_reltiming}reltiming(slcs, processdir)
{do_dembased}dembased(slcs, processdir)

{do_coregpm}coregpm(slcs, processdir)
{do_resample_hh}resample(slcs, processdir)

{do_tsx_reramp_hh}reramp_TSX(slcs, master, processdir)

#compute flat earth and dem reference phase only once for all polarizations
{do_comprefpha}comprefpha(slcs, processdir)
{do_comprefdem}comprefdem(slcs, processdir)

#from here all steps are performed per polarization
#this resample step should be located here, since the ifgs.res files is copied with the coregistration and reference phase parameters, but without the interferograms 
{do_resample_hv}resample(slcs, processdir, altimg='_HV')
{do_resample_vh}resample(slcs, processdir, altimg='_VH')
{do_resample_vv}resample(slcs, processdir, altimg='_VV')

{do_tsx_reramp_hv}reramp_TSX(slcs, master, processdir, altimg='_HV')
{do_tsx_reramp_vh}reramp_TSX(slcs, master, processdir, altimg='_VH')
{do_tsx_reramp_vv}reramp_TSX(slcs, master, processdir, altimg='_VV')

{do_interferogram_hh}interferogram(slcs, processdir)
{do_interferogram_hv}interferogram(slcs, processdir, altimg='_HV')
{do_interferogram_vh}interferogram(slcs, processdir, altimg='_VH')
{do_interferogram_vv}interferogram(slcs, processdir, altimg='_VV')

{do_subtrrefpha_hh}subtrrefpha(slcs, processdir)
{do_subtrrefpha_hv}subtrrefpha(slcs, processdir, altimg='_HV')
{do_subtrrefpha_vh}subtrrefpha(slcs, processdir, altimg='_VH')
{do_subtrrefpha_vv}subtrrefpha(slcs, processdir, altimg='_VV')

{do_subtrrefdem_hh}subtrrefdem(slcs, processdir)
{do_subtrrefdem_hv}subtrrefdem(slcs, processdir, altimg='_HV')
{do_subtrrefdem_vh}subtrrefdem(slcs, processdir, altimg='_VH')
{do_subtrrefdem_vv}subtrrefdem(slcs, processdir, altimg='_VV')

{do_coherence_hh}coherence(slcs, processdir)
{do_coherence_hv}coherence(slcs, processdir, altimg='_HV')
{do_coherence_vh}coherence(slcs, processdir, altimg='_VH')
{do_coherence_vv}coherence(slcs, processdir, altimg='_VV')


