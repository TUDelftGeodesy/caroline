from sys import argv, path
import os
import glob
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name, shape_AoI_name, version, caroline_dir = argv

search_parameters = ['coregistration_directory', 'shape_directory', 'track', 'asc_dsc', 'start_date', 'end_date',
                     'master_date', 'do_coarse_orbits',
                     'do_deramp', 'do_reramp', 'do_fake_fine_coreg_bursts', 'do_dac_bursts', 'do_fake_coreg_bursts',
                     'do_resample', 'do_reramp2',
                     'do_interferogram', 'do_compref_phase', 'do_compref_dem', 'do_coherence', 'do_esd',
                     'do_network_esd', 'do_ESD_correct',
                     'do_ref_phase', 'do_ref_dem', 'do_phasefilt', 'do_calc_coordinates', 'do_multilooking',
                     'do_unwrap', 'do_fake_master_resample', 'do_combine_master', 'do_combine_slave']
out_parameters = read_param_file(cpath, param_file, search_parameters)

base_stack = open("{}/caroline_v{}/files/doris_v5/doris_input.xml".format(caroline_dir, version))
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters['track'])
shape_dir = out_parameters['shape_directory']
doris_dir = out_parameters['coregistration_directory']
asc_dsc = eval(out_parameters['asc_dsc'])
start_date = out_parameters['start_date'].split("-")
start_date = eval(start_date[0] + start_date[1] + start_date[2])
end_date = out_parameters['end_date'].split("-")
end_date = eval(end_date[0] + end_date[1] + end_date[2])
master_date = out_parameters['master_date'].split("-")
master_date = eval(master_date[0] + master_date[1] + master_date[2])

do_coarse_orbits = "Yes" if eval(out_parameters['do_coarse_orbits']) == 1 else "No"
do_deramp = "Yes" if eval(out_parameters['do_deramp']) == 1 else "No"
do_reramp = "Yes" if eval(out_parameters['do_reramp']) == 1 else "No"
do_fake_fine_coreg_bursts = "Yes" if eval(out_parameters['do_fake_fine_coreg_bursts']) == 1 else "No"
do_dac_bursts = "Yes" if eval(out_parameters['do_dac_bursts']) == 1 else "No"
do_fake_coreg_bursts = "Yes" if eval(out_parameters['do_fake_coreg_bursts']) == 1 else "No"
do_fake_master_resample = "Yes" if eval(out_parameters['do_fake_master_resample']) == 1 else "No"
do_resample = "Yes" if eval(out_parameters['do_resample']) == 1 else "No"
do_reramp2 = "Yes" if eval(out_parameters['do_reramp2']) == 1 else "No"
do_interferogram = "Yes" if eval(out_parameters['do_interferogram']) == 1 else "No"
do_compref_phase = "Yes" if eval(out_parameters['do_compref_phase']) == 1 else "No"
do_compref_dem = "Yes" if eval(out_parameters['do_compref_dem']) == 1 else "No"
do_coherence = "Yes" if eval(out_parameters['do_coherence']) == 1 else "No"
do_esd = "Yes" if eval(out_parameters['do_esd']) == 1 else "No"
do_network_esd = "Yes" if eval(out_parameters['do_network_esd']) == 1 else "No"
do_ESD_correct = "Yes" if eval(out_parameters['do_ESD_correct']) == 1 else "No"
do_combine_master = "Yes" if eval(out_parameters['do_combine_master']) == 1 else "No"
do_combine_slave = "Yes" if eval(out_parameters['do_combine_slave']) == 1 else "No"
do_ref_phase = "Yes" if eval(out_parameters['do_ref_phase']) == 1 else "No"
do_ref_dem = "Yes" if eval(out_parameters['do_ref_dem']) == 1 else "No"
do_phasefilt = "Yes" if eval(out_parameters['do_phasefilt']) == 1 else "No"
do_calc_coordinates = "Yes" if eval(out_parameters['do_calc_coordinates']) == 1 else "No"
do_multilooking = "Yes" if eval(out_parameters['do_multilooking']) == 1 else "No"
do_unwrap = "Yes" if eval(out_parameters['do_unwrap']) == 1 else "No"

for track in range(len(tracks)):
    stack_dir = '{}/{}_s1_{}_t{:0>3d}/good_images/20*'.format(doris_dir, AoI_name, asc_dsc[track], tracks[track])
    image_links = glob.glob(stack_dir)
    images = list(sorted([eval(image.split("/")[-1]) for image in image_links]))
    act_start_date = str(min([image for image in images if image >= start_date]))
    act_end_date = str(max([image for image in images if image <= end_date]))
    act_master_date = str(min([image for image in images if image >= master_date]))

    doris_stack = stack.format(doris_dir=doris_dir, AoI_name=AoI_name, asc_dsc=asc_dsc[track],
                               shape_AoI_name=shape_AoI_name,
                               fill_track="{:0>3d}".format(tracks[track]),
                               track=tracks[track], shape_dir=shape_dir,
                               do_coarse_orbits=do_coarse_orbits,
                               do_deramp=do_deramp,
                               do_reramp=do_reramp,
                               do_fake_fine_coreg_bursts=do_fake_fine_coreg_bursts,
                               do_fake_master_resample=do_fake_master_resample,
                               do_dac_bursts=do_dac_bursts,
                               do_fake_coreg_bursts=do_fake_coreg_bursts,
                               do_resample=do_resample,
                               do_reramp2=do_reramp2,
                               do_interferogram=do_interferogram,
                               do_compref_phase=do_compref_phase,
                               do_compref_dem=do_compref_dem,
                               do_coherence=do_coherence,
                               do_esd=do_esd,
                               do_network_esd=do_network_esd,
                               do_ESD_correct=do_ESD_correct,
                               do_combine_master=do_combine_master,
                               do_combine_slave=do_combine_slave,
                               do_ref_phase=do_ref_phase,
                               do_ref_dem=do_ref_dem,
                               do_phasefilt=do_phasefilt,
                               do_calc_coordinates=do_calc_coordinates,
                               do_multilooking=do_multilooking,
                               do_unwrap=do_unwrap,
                               start_date="{}-{}-{}".format(act_start_date[:4], act_start_date[4:6],
                                                            act_start_date[6:]),
                               end_date="{}-{}-{}".format(act_end_date[:4], act_end_date[4:6], act_end_date[6:]),
                               master_date="{}-{}-{}".format(act_master_date[:4], act_master_date[4:6],
                                                             act_master_date[6:]))

    fw = open("{}/{}_s1_{}_t{:0>3d}/doris_input.xml".format(out_parameters['coregistration_directory'], AoI_name,
                                                            asc_dsc[track], tracks[track]), 'w')
    fw.write(doris_stack)
    fw.close()
