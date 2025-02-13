from sys import argv
from read_param_file import read_param_file
import glob

try:
    filename, param_file, cpath, slurm_job_id = argv

    search_parameters = ['track', 'asc_dsc', 'do_coregistration', 'do_crop', 'do_depsi', 'do_depsi_post', 'sensor',
                         'coregistration_directory', 'crop_directory', 'depsi_directory', 'do_reslc',
                         'reslc_directory', 'skygeo_viewer', 'coregistration_AoI_name',
                         'crop_AoI_name', 'depsi_AoI_name', 'reslc_AoI_name']
    out_parameters = read_param_file(cpath, param_file, search_parameters)

    tracks = eval(out_parameters['track'])
    asc_dsc = eval(out_parameters['asc_dsc'])

    tracks_formatted = []
    for i in range(len(tracks)):
        tracks_formatted.append('{}_t{}'.format(asc_dsc[i], "{:0>3d}".format(tracks[i])))

    if len(tracks_formatted) == 1:
        tracks_formatted = tracks_formatted[0]

    run_id = param_file.split('_spider_')[1].split('/')[0][:-16]

    f = open(f'{cpath}/{param_file}')
    paramfile = f.read()
    f.close()

    log = "==========DEBUG LOGS===========\n\n"
    log += f"CAROLINE Slurm output: {cpath}/slurm-{slurm_job_id}.out\n\n"

    success_rates = {'do_coregistration': [[], []],
                     'do_crop': [[], []],
                     'do_reslc': [[], []],
                     'do_depsi': [[], []],
                     'do_depsi_post': [[], []]}
    for step in ['do_coregistration', 'do_crop', 'do_reslc', 'do_depsi', 'do_depsi_post']:
        if out_parameters[step] == '1':
            if step == 'do_coregistration':
                if out_parameters['sensor'] == 'S1':
                    log += '\n\n---------DORIS v5--------\n\n'
                    for track in range(len(tracks)):
                        log += f'---Track {tracks[track]}_{asc_dsc[track]}---\n\n'
                        status_file = None
                        slurm_file = None
                        dir_file = "{}/{}_s1_{}_t{:0>3d}/dir_contents.txt".format(
                            out_parameters['coregistration_directory'],
                            out_parameters['coregistration_AoI_name'],
                            asc_dsc[track], tracks[track])
                        f = open(dir_file)
                        prev_dir_contents = f.read().split('\n')
                        f.close()
                        profile_logs = glob.glob("{}/{}_s1_{}_t{:0>3d}/profile_log*".format(
                            out_parameters['coregistration_directory'], out_parameters['coregistration_AoI_name'],
                            asc_dsc[track], tracks[track]))
                        slurms = glob.glob("{}/{}_s1_{}_t{:0>3d}/slurm*.out".format(
                            out_parameters['coregistration_directory'], out_parameters['coregistration_AoI_name'],
                            asc_dsc[track], tracks[track]))
                        for profile_log in profile_logs:
                            if profile_log.split('/')[-1] not in prev_dir_contents:
                                status_file = profile_log
                                break
                        for slurm in list(sorted(list(slurms))):
                            if slurm.split('/')[-1] not in prev_dir_contents:
                                slurm_file = slurm
                                break

                        if status_file is not None:
                            f = open(status_file)
                            status = f.read()
                            f.close()

                            if ' : end' in status:
                                success_rates[step][0].append(
                                    f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                                log += 'Step finished successfully!\n\n'
                            else:
                                success_rates[step][1].append(
                                    f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                                log += '!!! Step did not finish properly!\n\n'
                        else:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += '!!! Step did not start properly!\n\n'

                        log += f'Profile log: {status_file}\nSlurm output: {slurm_file}\n\n'

                        if status_file is not None:
                            f = open(status_file)
                            status = f.read()
                            f.close()
                            log += f'Profile log output:\n'
                            log += status
                            log += '\n\n'

                else:
                    log += '\n\n---------DeInSAR---------\n\n'
                    for track in range(len(tracks)):
                        log += f'---Track {tracks[track]}_{asc_dsc[track]}---\n\n'

                        slurm_file = None
                        dir_file = "{}/{}_s1_{}_t{:0>3d}/dir_contents.txt".format(
                            out_parameters['stitch_directory'],
                            out_parameters['stitch_AoI_name'],
                            asc_dsc[track], tracks[track])
                        f = open(dir_file)
                        prev_dir_contents = f.read().split('\n')
                        f.close()
                        slurms = glob.glob("{}/{}_s1_{}_t{:0>3d}/slurm*.out".format(
                            out_parameters['stitch_directory'], out_parameters['stitch_AoI_name'],
                            asc_dsc[track], tracks[track]))
                        for slurm in slurms:
                            if slurm.split('/')[-1] not in prev_dir_contents:
                                slurm_file = slurm
                                break

                        if slurm_file is not None:
                            f = open(slurm_file)
                            status = f.read()
                            f.close()

                            if 'Traceback (most recent call last):' in status:
                                success_rates[step][1].append(
                                    f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                                log += '!!! Step did not finish properly!\n\n'
                            else:
                                success_rates[step][0].append(
                                    f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                                log += 'Step finished successfully!\n\n'
                        else:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += '!!! Step did not start properly!\n\n'

                        log += f'Slurm output: {slurm_file}\n\n'

            elif step == 'do_crop':
                log += '\n\n---------Cropping---------\n\n'
                for track in range(len(tracks)):
                    log += f'---Track {tracks[track]}_{asc_dsc[track]}---\n\n'

                    slurm_file = None
                    dir_file = "{}/{}_s1_{}_t{:0>3d}/dir_contents.txt".format(
                        out_parameters['crop_directory'],
                        out_parameters['crop_AoI_name'],
                        asc_dsc[track], tracks[track])
                    f = open(dir_file)
                    prev_dir_contents = f.read().split('\n')
                    f.close()
                    slurms = glob.glob("{}/{}_s1_{}_t{:0>3d}/slurm*.out".format(
                        out_parameters['crop_directory'], out_parameters['crop_AoI_name'],
                        asc_dsc[track], tracks[track]))
                    for slurm in list(sorted(list(slurms))):
                        if slurm.split('/')[-1] not in prev_dir_contents:
                            slurm_file = slurm
                            break

                    if slurm_file is not None:
                        f = open(slurm_file)
                        status = f.read()
                        f.close()

                        if 'Error in ' in status:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += '!!! Step did not finish properly!\n\n'
                        else:
                            success_rates[step][0].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += 'Step finished successfully!\n\n'
                    else:
                        success_rates[step][1].append(
                            f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                        log += '!!! Step did not start properly!\n\n'

                    log += f'Slurm output: {slurm_file}\n\n'

            elif step == 'do_reslc':
                log += '\n\n---------Re-SLC---------\n\n'
                for track in range(len(tracks)):
                    log += f'---Track {tracks[track]}_{asc_dsc[track]}---\n\n'

                    slurm_file = None
                    dir_file = "{}/{}_s1_{}_t{:0>3d}/dir_contents.txt".format(
                        out_parameters['reslc_directory'],
                        out_parameters['reslc_AoI_name'],
                        asc_dsc[track], tracks[track])
                    f = open(dir_file)
                    prev_dir_contents = f.read().split('\n')
                    f.close()
                    slurms = glob.glob("{}/{}_s1_{}_t{:0>3d}/slurm*.out".format(
                        out_parameters['reslc_directory'], out_parameters['reslc_AoI_name'],
                        asc_dsc[track], tracks[track]))
                    for slurm in list(sorted(list(slurms))):
                        if slurm.split('/')[-1] not in prev_dir_contents:
                            slurm_file = slurm  # it's the first one
                            break

                    if slurm_file is not None:
                        f = open(slurm_file)
                        status = f.read()
                        f.close()

                        if 'Finishing... Closing client.' not in status:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += '!!! Step did not finish properly!\n\n'
                        else:
                            success_rates[step][0].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += 'Step finished successfully!\n\n'
                    else:
                        success_rates[step][1].append(
                            f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                        log += '!!! Step did not start properly!\n\n'

                    log += f'Slurm output: {slurm_file}\n\n'

                    if slurm_file is not None:
                        f = open(slurm_file)
                        status = f.read()
                        f.close()
                        log += f'Scheduler Slurm output:\n'
                        log += status
                        log += '\n\n'

            elif step == 'do_depsi':
                log += '\n\n---------DePSI--------\n\n'
                for track in range(len(tracks)):
                    log += f'---Track {tracks[track]}_{asc_dsc[track]}---\n\n'
                    status_file = None
                    slurm_file = None
                    dir_file = "{}/{}_s1_{}_t{:0>3d}/psi/dir_contents.txt".format(
                        out_parameters['depsi_directory'],
                        out_parameters['depsi_AoI_name'],
                        asc_dsc[track], tracks[track])
                    f = open(dir_file)
                    prev_dir_contents = f.read().split('\n')
                    f.close()
                    resfiles = glob.glob("{}/{}_s1_{}_t{:0>3d}/psi/*resfile.txt".format(
                        out_parameters['depsi_directory'], out_parameters['depsi_AoI_name'],
                        asc_dsc[track], tracks[track]))
                    slurms = glob.glob("{}/{}_s1_{}_t{:0>3d}/psi/slurm*.out".format(
                        out_parameters['depsi_directory'], out_parameters['depsi_AoI_name'],
                        asc_dsc[track], tracks[track]))
                    for resfile in resfiles:
                        if resfile.split('/')[-1] not in prev_dir_contents:
                            status_file = resfile
                            break
                    for slurm in list(sorted(list(slurms))):
                        if slurm.split('/')[-1] not in prev_dir_contents:
                            slurm_file = slurm  # it's the first one
                            break

                    if status_file is not None:
                        f = open(status_file)
                        status = f.read()
                        f.close()

                        if 'group8, end spatio-temporal consistency.' in status:
                            success_rates[step][0].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += 'Step finished successfully!\n\n'
                        else:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += '!!! Step did not finish properly!\n\n'
                    else:
                        success_rates[step][1].append(
                            f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                        log += '!!! Step did not start properly!\n\n'

                    log += f'Resfile: {status_file}\nSlurm output: {slurm_file}\n\n'

                    if status_file is not None:
                        f = open(status_file)
                        status = f.read()
                        f.close()
                        log += f'Resfile output:\n'
                        log += status
                        log += '\n\n'

            elif step == 'do_depsi_post':
                log += '\n\n---------DePSI-post--------\n\n'
                for track in range(len(tracks)):
                    log += f'---Track {tracks[track]}_{asc_dsc[track]}---\n\n'
                    status_file = None
                    slurm_file = None
                    dir_file = "{}/{}_s1_{}_t{:0>3d}/psi/dir_contents_depsi_post.txt".format(
                        out_parameters['depsi_directory'],
                        out_parameters['depsi_AoI_name'],
                        asc_dsc[track], tracks[track])
                    f = open(dir_file)
                    prev_dir_contents = f.read().split('\n')
                    f.close()

                    slurms = glob.glob("{}/{}_s1_{}_t{:0>3d}/psi/slurm*.out".format(
                        out_parameters['depsi_directory'], out_parameters['depsi_AoI_name'],
                        asc_dsc[track], tracks[track]))

                    for slurm in list(sorted(list(slurms))):
                        if slurm.split('/')[-1] not in prev_dir_contents:
                            slurm_file = slurm  # it's the first one
                            break

                    if slurm_file is not None:
                        f = open(slurm_file)
                        status = f.read()
                        f.close()

                        if 'Write csv web portal file ...' in status:
                            success_rates[step][0].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += 'Step finished successfully!\n\n'
                        else:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                            log += '!!! Step did not finish properly!\n\n'
                    else:
                        success_rates[step][1].append(
                            f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{"{:0>3d}".format(tracks[track])}')
                        log += '!!! Step did not start properly!\n\n'

                    log += f'Slurm output: {slurm_file}\n\n'
    log += '================'


    def print_mail(run_id, track, sensor, dv5, crop, depsi, dppu, portal_link, coreg_dir, crop_dir, depsi_dir,
                   depsipost_dir, reslc, reslcdir, paramfile, param_file, logs, coreg_correct, crop_correct,
                   reslc_correct, depsi_correct, dp_correct):
        print("""Dear radargroup,
    
    A new CAROLINE run has just finished on run {run_id}! 
    
    The characteristics of this run are:
    Track(s): {tracks}
    Sensor: {sensor}
    
    The following steps were run:
    Coregistration: {dv5} {coreg_correct} {coreg_dir}
    
    Cropping: {crop} {crop_correct} {crop_dir}
    Re-SLC: {reslc} {reslc_correct} {reslc_dir}
    
    Depsi: {depsi} {depsi_correct} {depsi_dir}
    Depsi-post & portal upload: {dppu} {dp_correct} {depsipost_dir}
    
    {portal_link}
    
    In case of questions, please contact Niels at n.h.jansen@tudelft.nl or Simon at s.a.n.vandiepen@tudelft.nl
    
    Kind regards,
    The CAROLINE development team,
    Freek, Niels, and Simon
    
    =======================================
    ===========DEBUG info==================
    =======================================
    First logs of the subprocesses, then the parameter file.
    =======================================
    
    {logs}
    
    --- PARAMETER FILE: {param_file} ---
    {paramfile}""".format(tracks=track,
                          sensor=sensor,
                          dv5=dv5,
                          crop=crop,
                          depsi=depsi,
                          dppu=dppu,
                          run_id=run_id,
                          portal_link=portal_link,
                          coreg_dir=coreg_dir,
                          crop_dir=crop_dir,
                          depsi_dir=depsi_dir,
                          depsipost_dir=depsipost_dir,
                          reslc=reslc,
                          reslc_dir=reslcdir,
                          paramfile=paramfile,
                          param_file=param_file,
                          logs=logs,
                          coreg_correct=coreg_correct,
                          crop_correct=crop_correct,
                          reslc_correct=reslc_correct,
                          depsi_correct=depsi_correct,
                          dp_correct=dp_correct))


    print_mail(run_id=run_id,
               track=tracks_formatted,
               sensor=out_parameters['sensor'],
               dv5="Yes" if eval(out_parameters['do_coregistration']) == 1 else "No",
               crop="Yes" if eval(out_parameters['do_crop']) == 1 else "No",
               depsi="Yes" if eval(out_parameters['do_depsi']) == 1 else "No",
               dppu="Yes" if eval(out_parameters['do_depsi_post']) == 1 else "No",
               portal_link=f"NOTE: it can take a few hours for the results to show up in the portal.\nThe DePSI-post results can be accessed at https://caroline.portal-tud.skygeo.com/portal/caroline/{out_parameters['skygeo_viewer']} ." if eval(
                   out_parameters['do_depsi_post']) == 1 else "",
               coreg_dir=f"(located in {out_parameters['coregistration_directory']} )" if eval(
                   out_parameters['do_coregistration']) == 1 else "",
               crop_dir=f"(located in {out_parameters['crop_directory']} )" if eval(
                   out_parameters['do_crop']) == 1 else "",
               depsi_dir=f"(located in {out_parameters['depsi_directory']} )" if eval(
                   out_parameters['do_depsi']) == 1 else "",
               depsipost_dir=f"(located in {out_parameters['depsi_directory']} )" if eval(
                   out_parameters['do_depsi_post']) == 1 else "",
               reslc="Yes" if eval(out_parameters['do_reslc']) == 1 else "No",
               reslcdir=f"(located in {out_parameters['reslc_directory']} )" if eval(
                   out_parameters['do_reslc']) == 1 else "",
               paramfile=paramfile,
               param_file=f"{cpath}/{param_file}",
               logs=log,
               coreg_correct=f"(Proper finish: {success_rates['do_coregistration'][0]}, improper finish: {success_rates['do_coregistration'][1]} )" if eval(
                   out_parameters['do_coregistration']) == 1 else "",
               crop_correct=f"(Proper finish: {success_rates['do_crop'][0]}, improper finish: {success_rates['do_crop'][1]} )" if eval(
                   out_parameters['do_crop']) == 1 else "",
               reslc_correct=f"(Proper finish: {success_rates['do_reslc'][0]}, improper finish: {success_rates['do_reslc'][1]} )" if eval(
                   out_parameters['do_reslc']) == 1 else "",
               depsi_correct=f"(Proper finish: {success_rates['do_depsi'][0]}, improper finish: {success_rates['do_depsi'][1]} )" if eval(
                   out_parameters['do_depsi']) == 1 else "",
               dp_correct=f"(Proper finish: {success_rates['do_depsi_post'][0]}, improper finish: {success_rates['do_depsi_post'][1]} )" if eval(
                   out_parameters['do_depsi_post']) == 1 else "")

except Exception as e:
    print(f"""Dear radargroup,

It appears the CAROLINE email generation has encountered an error. Please create an issue on the CAROLINE GitHub project
https://github.com/TUDelftGeodesy/caroline/issues mentioning:
1) that the email generation failed
2) the subject of this mail
3) the following error message:

{e}


Please add the labels Priority-0 and bug, and assign Simon.

Thank you in advance, and sorry for the inconvenience.

Kind regards,
The CAROLINE development team,
Freek, Niels, and Simon

""")
