from sys import argv, path
import os
import glob
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, version, caroline_dir = argv

search_parameters = ['sensor', 'polarisation', 'di_do_orbit', 'coregistration_directory',
                     'coregistration_AoI_name', 'track', 'asc_dsc', 'di_do_crop', 'di_do_tsx_deramp', 'di_do_simamp',
                     'di_do_mtiming', 'di_do_ovs', 'di_do_choose_master', 'di_do_coarseorb', 'di_do_coarsecorr',
                     'di_do_finecoreg', 'di_do_reltiming', 'di_do_dembased', 'di_do_coregpm', 'di_do_resample',
                     'di_do_tsx_reramp', 'di_do_interferogram', 'di_do_subtrrefpha', 'di_do_subtrrefdem',
                     'di_do_coherence', 'di_data_directories', 'start_date', 'end_date', 'master_date',
                     'di_do_comprefdem', 'di_do_comprefpha', 'di_do_geocoding']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])
datadirs = eval(out_parameters['di_data_directories'])
polarisation = eval(out_parameters['polarisation'])
start_date = out_parameters['start_date'].split("-")
start_date = eval(start_date[0] + start_date[1] + start_date[2])
end_date = out_parameters['end_date'].split("-")
end_date = eval(end_date[0] + end_date[1] + end_date[2])
master_date = out_parameters['master_date'].split("-")
master_date = eval(master_date[0] + master_date[1] + master_date[2])

if len(tracks) != len(datadirs):
    raise ValueError(f'Got {len(tracks)} tracks but {len(datadirs)} data directories!')

if out_parameters['sensor'] != 'TSX':
    if out_parameters['di_do_tsx_deramp'] == '1':
        print(f'WARNING: do_TSX_deramp is set to 1 while sensor is {out_parameters["sensor"]}. Ignoring...')
        out_parameters['di_do_tsx_deramp'] = '0'
    if out_parameters['di_do_tsx_reramp'] == '1':
        print(f'WARNING: do_TSX_reramp is set to 1 while sensor is {out_parameters["sensor"]}. Ignoring...')
        out_parameters['di_do_tsx_reramp'] = '0'

if out_parameters['di_do_orbit'] == '1' and out_parameters['sensor'] not in ['ENV', 'ERS', 'RSAT2']:
    print(f'WARNING: do_orbit is set to 1 while sensor is {out_parameters["sensor"]}. Ignoring...')
    out_parameters['di_do_orbit'] = '0'

# TODO: Fix that this is not necessary
if 'HH' not in polarisation:
    print(f'WARNING: requested polarisations {polarisation}, but this is not implemented without HH. Adding HH...')
    polarisation.append('HH')

fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/run_deinsar.py", "r")
base_data = fr.read()
fr.close()

# Set correct parameters to input in base_data (non-active functions are commented out with #)

do_orbit = '' if out_parameters['di_do_orbit'] == '1' else '#'
do_crop_hh = '' if (out_parameters['di_do_crop'] == '1' and 'HH' in polarisation) else '#'
do_crop_hv = '' if (out_parameters['di_do_crop'] == '1' and 'HV' in polarisation) else '#'
do_crop_vh = '' if (out_parameters['di_do_crop'] == '1' and 'VH' in polarisation) else '#'
do_crop_vv = '' if (out_parameters['di_do_crop'] == '1' and 'VV' in polarisation) else '#'
do_tsx_deramp_hh = '' if (out_parameters['di_do_tsx_deramp'] == '1' and 'HH' in polarisation) else '#'
do_tsx_deramp_hv = '' if (out_parameters['di_do_tsx_deramp'] == '1' and 'HV' in polarisation) else '#'
do_tsx_deramp_vh = '' if (out_parameters['di_do_tsx_deramp'] == '1' and 'VH' in polarisation) else '#'
do_tsx_deramp_vv = '' if (out_parameters['di_do_tsx_deramp'] == '1' and 'VV' in polarisation) else '#'
do_simamp = '' if out_parameters['di_do_simamp'] == '1' else '#'
do_mtiming = '' if out_parameters['di_do_mtiming'] == '1' else '#'
do_ovs_hh = '' if (out_parameters['di_do_ovs'] == '1' and 'HH' in polarisation) else '#'
do_ovs_hv = '' if (out_parameters['di_do_ovs'] == '1' and 'HV' in polarisation) else '#'
do_ovs_vh = '' if (out_parameters['di_do_ovs'] == '1' and 'VH' in polarisation) else '#'
do_ovs_vv = '' if (out_parameters['di_do_ovs'] == '1' and 'VV' in polarisation) else '#'
do_choose_master_hh = '' if (out_parameters['di_do_choose_master'] == '1' and 'HH' in polarisation) else '#'
do_choose_master_hv = '' if (out_parameters['di_do_choose_master'] == '1' and 'HV' in polarisation) else '#'
do_choose_master_vh = '' if (out_parameters['di_do_choose_master'] == '1' and 'VH' in polarisation) else '#'
do_choose_master_vv = '' if (out_parameters['di_do_choose_master'] == '1' and 'VV' in polarisation) else '#'
do_coarseorb = '' if out_parameters['di_do_coarseorb'] == '1' else '#'
do_coarsecorr = '' if out_parameters['di_do_coarsecorr'] == '1' else '#'
do_finecoreg = '' if out_parameters['di_do_finecoreg'] == '1' else '#'
do_reltiming = '' if out_parameters['di_do_reltiming'] == '1' else '#'
do_dembased = '' if out_parameters['di_do_dembased'] == '1' else '#'
do_coregpm = '' if out_parameters['di_do_coregpm'] == '1' else '#'
do_comprefpha = '' if out_parameters['di_do_comprefpha'] == '1' else '#'
do_comprefdem = '' if out_parameters['di_do_comprefdem'] == '1' else '#'
do_resample_hh = '' if (out_parameters['di_do_resample'] == '1' and 'HH' in polarisation) else '#'
do_resample_hv = '' if (out_parameters['di_do_resample'] == '1' and 'HV' in polarisation) else '#'
do_resample_vh = '' if (out_parameters['di_do_resample'] == '1' and 'VH' in polarisation) else '#'
do_resample_vv = '' if (out_parameters['di_do_resample'] == '1' and 'VV' in polarisation) else '#'
do_tsx_reramp_hh = '' if (out_parameters['di_do_tsx_reramp'] == '1' and 'HH' in polarisation) else '#'
do_tsx_reramp_hv = '' if (out_parameters['di_do_tsx_reramp'] == '1' and 'HV' in polarisation) else '#'
do_tsx_reramp_vh = '' if (out_parameters['di_do_tsx_reramp'] == '1' and 'VH' in polarisation) else '#'
do_tsx_reramp_vv = '' if (out_parameters['di_do_tsx_reramp'] == '1' and 'VV' in polarisation) else '#'
do_interferogram_hh = '' if (out_parameters['di_do_interferogram'] == '1' and 'HH' in polarisation) else '#'
do_interferogram_hv = '' if (out_parameters['di_do_interferogram'] == '1' and 'HV' in polarisation) else '#'
do_interferogram_vh = '' if (out_parameters['di_do_interferogram'] == '1' and 'VH' in polarisation) else '#'
do_interferogram_vv = '' if (out_parameters['di_do_interferogram'] == '1' and 'VV' in polarisation) else '#'
do_subtrrefpha_hh = '' if (out_parameters['di_do_subtrrefpha'] == '1' and 'HH' in polarisation) else '#'
do_subtrrefpha_hv = '' if (out_parameters['di_do_subtrrefpha'] == '1' and 'HV' in polarisation) else '#'
do_subtrrefpha_vh = '' if (out_parameters['di_do_subtrrefpha'] == '1' and 'VH' in polarisation) else '#'
do_subtrrefpha_vv = '' if (out_parameters['di_do_subtrrefpha'] == '1' and 'VV' in polarisation) else '#'
do_subtrrefdem_hh = '' if (out_parameters['di_do_subtrrefdem'] == '1' and 'HH' in polarisation) else '#'
do_subtrrefdem_hv = '' if (out_parameters['di_do_subtrrefdem'] == '1' and 'HV' in polarisation) else '#'
do_subtrrefdem_vh = '' if (out_parameters['di_do_subtrrefdem'] == '1' and 'VH' in polarisation) else '#'
do_subtrrefdem_vv = '' if (out_parameters['di_do_subtrrefdem'] == '1' and 'VV' in polarisation) else '#'
do_coherence_hh = '' if (out_parameters['di_do_coherence'] == '1' and 'HH' in polarisation) else '#'
do_coherence_hv = '' if (out_parameters['di_do_coherence'] == '1' and 'HV' in polarisation) else '#'
do_coherence_vh = '' if (out_parameters['di_do_coherence'] == '1' and 'VH' in polarisation) else '#'
do_coherence_vv = '' if (out_parameters['di_do_coherence'] == '1' and 'VV' in polarisation) else '#'
do_geocoding = '' if out_parameters['di_do_geocoding'] == '1' else '#'

for track in range(len(tracks)):
    basedir = "{}/{}_{}_{}_t{:0>3d}".format(out_parameters['coregistration_directory'],
                                            out_parameters['coregistration_AoI_name'],
                                            out_parameters['sensor'].lower(), asc_dsc[track],
                                            tracks[track])

    datadir = datadirs[track]
    if out_parameters['sensor'] in ['ALOS2', 'ERS']:
        dirs = glob.glob(f'{datadir}/[12]*')
        images = list(sorted([eval(image.split("/")[-1]) for image in dirs]))
    elif out_parameters['sensor'] in ['RSAT2']:
        dirs = glob.glob(f'{datadir}/RS2*')
        images = list(sorted([eval(image.split('/')[-1].split('FQ2_')[1].split('_')[0]) for image in dirs]))
    elif out_parameters['sensor'] in ['TSX']:
        dirs = glob.glob(f'{datadir}/*/iif/*')
        images = list(sorted([eval(image.split('/')[-1].split('SRA_')[1].split('T')[0]) for image in dirs]))
    elif out_parameters['sensor'] in ['SAOCOM']:
        dirs = glob.glob(f'{datadir}/*/*.xemt')
        images = list(sorted([eval(image.split('/')[-1].split('OLF_')[1].split('T')[0]) for image in dirs]))
    elif out_parameters['sensor'] in ['ENV']:
        # 2 different formats for some reason
        dirs1 = glob.glob(f'{datadir}/*.N1')
        dirs2 = glob.glob(f'{datadir}/*/*.N1')
        dirs = []
        for d in dirs1:
            dirs.append(d)
        for d in dirs2:
            dirs.append(d)
        images = list(sorted([eval(image.split('/')[-1].split('PA')[1].split('_')[0]) for image in dirs]))
    else:
        raise ValueError(f'Unknown directory format for sensor {out_parameters["sensor"]}!')
    act_start_date = str(min([image for image in images if image >= start_date]))
    act_end_date = str(max([image for image in images if image <= end_date]))
    act_master_date = str(min([image for image in images if image >= master_date]))

    data = base_data.format(datadir=datadir,
                            master=act_master_date,
                            startdate=act_start_date,
                            enddate=act_end_date,
                            sensor=out_parameters['sensor'],
                            do_orbit=do_orbit,
                            do_crop_hh=do_crop_hh,
                            do_crop_hv=do_crop_hv,
                            do_crop_vh=do_crop_vh,
                            do_crop_vv=do_crop_vv,
                            do_tsx_deramp_hh=do_tsx_deramp_hh,
                            do_tsx_deramp_hv=do_tsx_deramp_hv,
                            do_tsx_deramp_vh=do_tsx_deramp_vh,
                            do_tsx_deramp_vv=do_tsx_deramp_vv,
                            do_simamp=do_simamp,
                            do_mtiming=do_mtiming,
                            do_ovs_hh=do_ovs_hh,
                            do_ovs_hv=do_ovs_hv,
                            do_ovs_vh=do_ovs_vh,
                            do_ovs_vv=do_ovs_vv,
                            do_choose_master_hh=do_choose_master_hh,
                            do_choose_master_hv=do_choose_master_hv,
                            do_choose_master_vh=do_choose_master_vh,
                            do_choose_master_vv=do_choose_master_vv,
                            do_coarseorb=do_coarseorb,
                            do_coarsecorr=do_coarsecorr,
                            do_finecoreg=do_finecoreg,
                            do_reltiming=do_reltiming,
                            do_dembased=do_dembased,
                            do_coregpm=do_coregpm,
                            do_resample_hh=do_resample_hh,
                            do_tsx_reramp_hh=do_tsx_reramp_hh,
                            do_comprefdem=do_comprefdem,
                            do_comprefpha=do_comprefpha,
                            do_resample_hv=do_resample_hv,
                            do_resample_vh=do_resample_vh,
                            do_resample_vv=do_resample_vv,
                            do_tsx_reramp_hv=do_tsx_reramp_hv,
                            do_tsx_reramp_vh=do_tsx_reramp_vh,
                            do_tsx_reramp_vv=do_tsx_reramp_vv,
                            do_interferogram_hh=do_interferogram_hh,
                            do_interferogram_hv=do_interferogram_hv,
                            do_interferogram_vh=do_interferogram_vh,
                            do_interferogram_vv=do_interferogram_vv,
                            do_subtrrefpha_hh=do_subtrrefpha_hh,
                            do_subtrrefpha_hv=do_subtrrefpha_hv,
                            do_subtrrefpha_vh=do_subtrrefpha_vh,
                            do_subtrrefpha_vv=do_subtrrefpha_vv,
                            do_subtrrefdem_hh=do_subtrrefdem_hh,
                            do_subtrrefdem_hv=do_subtrrefdem_hv,
                            do_subtrrefdem_vh=do_subtrrefdem_vh,
                            do_subtrrefdem_vv=do_subtrrefdem_vv,
                            do_coherence_hh=do_coherence_hh,
                            do_coherence_hv=do_coherence_hv,
                            do_coherence_vh=do_coherence_vh,
                            do_coherence_vv=do_coherence_vv,
                            do_geocoding=do_geocoding)

    fw = open(f"{basedir}/run_deinsar.py", "w")
    fw.write(data)
    fw.close()
