from sys import argv
filename, param_file, cpath, AoI_name, version = argv

import glob

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['doris_directory', 'shape_directory', 'track','asc_dsc', 'start_date', 'end_date', 'master_date', 'do_coarse_orbits',
	    	     'do_deramp', 'do_reramp', 'do_fake_fine_coreg_bursts', 'do_dac_bursts', 'do_fake_coreg_bursts', 'do_resample', 'do_reramp2',
		     'do_interferogram', 'do_compref_phase', 'do_compref_dem', 'do_coherence', 'do_esd', 'do_network_esd', 'do_ESD_correct', 
		     'do_ref_phase', 'do_ref_dem', 'do_phasefilt', 'do_calc_coordinates', 'do_multilooking', 'do_unwrap']
out_parameters = []


for param in search_parameters:
    found = False
    for p in parameters:
	if param in p:
	    do = p.split("=")[1]
	    if "#" in do:
		do = do.split("#")[0]
	    do = do.strip().strip("'").strip('"')
	    out_parameters.append(do)
	    found = True
	    break
    if not found:
	raise ValueError("{} not found!!".format(param))

base_stack = open("/home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v{}/files/doris_v5/doris_input.xml".format(version))
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters[2])
shape_dir = out_parameters[1]
doris_dir = out_parameters[0]
asc_dsc = eval(out_parameters[3])
start_date = out_parameters[4].split("-")
start_date = eval(start_date[0]+start_date[1]+start_date[2])
end_date = out_parameters[5].split("-")
end_date = eval(end_date[0]+end_date[1]+end_date[2])
master_date = out_parameters[6].split("-")
master_date = eval(master_date[0]+master_date[1]+master_date[2])

do_coarse_orbits="Yes" if eval(out_parameters[7]) == 1 else "No"
do_deramp="Yes" if eval(out_parameters[8]) == 1 else "No"
do_reramp="Yes" if eval(out_parameters[9]) == 1 else "No"
do_fake_fine_coreg_bursts="Yes" if eval(out_parameters[10]) == 1 else "No"
do_dac_bursts="Yes" if eval(out_parameters[11]) == 1 else "No"
do_fake_coreg_bursts="Yes" if eval(out_parameters[12]) == 1 else "No"
do_resample="Yes" if eval(out_parameters[13]) == 1 else "No"
do_reramp2="Yes" if eval(out_parameters[14]) == 1 else "No"
do_interferogram="Yes" if eval(out_parameters[15]) == 1 else "No"
do_compref_phase="Yes" if eval(out_parameters[16]) == 1 else "No"
do_compref_dem="Yes" if eval(out_parameters[17]) == 1 else "No"
do_coherence="Yes" if eval(out_parameters[18]) == 1 else "No"
do_esd="Yes" if eval(out_parameters[19]) == 1 else "No"
do_network_esd="Yes" if eval(out_parameters[20]) == 1 else "No"
do_ESD_correct="Yes" if eval(out_parameters[21]) == 1 else "No"
do_ref_phase="Yes" if eval(out_parameters[22]) == 1 else "No"
do_ref_dem="Yes" if eval(out_parameters[23]) == 1 else "No"
do_phasefilt="Yes" if eval(out_parameters[24]) == 1 else "No"
do_calc_coordinates="Yes" if eval(out_parameters[25]) == 1 else "No"
do_multilooking="Yes" if eval(out_parameters[26]) == 1 else "No"
do_unwrap="Yes" if eval(out_parameters[27]) == 1 else "No"



for track in range(len(tracks)):

    stack_dir = '{}/{}_s1_{}_t{:0>3d}/good_images/20*'.format(doris_dir,AoI_name,asc_dsc[track],tracks[track])
    image_links = glob.glob(stack_dir)
    images = list(sorted([eval(image.split("/")[-1]) for image in image_links]))
    act_start_date = str(min([image for image in images if image >= start_date]))
    act_end_date = str(max([image for image in images if image <= end_date]))
    act_master_date = str(min([image for image in images if image >= master_date]))

    doris_stack = stack.format(doris_dir=doris_dir,AoI_name=AoI_name,asc_dsc=asc_dsc[track],fill_track="{:0>3d}".format(tracks[track]),
track=tracks[track],shape_dir=shape_dir,
do_coarse_orbits=do_coarse_orbits,
do_deramp=do_deramp,
do_reramp=do_reramp,
do_fake_fine_coreg_bursts=do_fake_fine_coreg_bursts,
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
do_ref_phase=do_ref_phase,
do_ref_dem=do_ref_dem,
do_phasefilt=do_phasefilt,
do_calc_coordinates=do_calc_coordinates,
do_multilooking=do_multilooking,
do_unwrap=do_unwrap,
start_date="{}-{}-{}".format(act_start_date[:4],act_start_date[4:6],act_start_date[6:]),
end_date="{}-{}-{}".format(act_end_date[:4],act_end_date[4:6],act_end_date[6:]),
master_date="{}-{}-{}".format(act_master_date[:4],act_master_date[4:6],act_master_date[6:]))

    fw = open("{}/{}_s1_{}_t{:0>3d}/doris_input.xml".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track]), 'w')
    fw.write(doris_stack)
    fw.close()



