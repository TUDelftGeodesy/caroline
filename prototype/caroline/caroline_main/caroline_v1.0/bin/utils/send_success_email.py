from sys import argv
from read_param_file import read_param_file
filename, param_file, cpath = argv

search_parameters = ['track', 'asc_dsc', 'do_doris', 'do_stack_stitching', 'do_depsi', 'do_depsi_post']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

tracks_formatted = []
for i in range(len(tracks)):
    tracks_formatted.append('{}_t{}'.format(asc_dsc[i], "{:0>3d}".format(tracks[i])))

if len(tracks_formatted) == 1:
    tracks_formatted = tracks_formatted[0]

run_id = param_file.split('_spider_')[1].split('_')[:2]
run_id = f'{run_id[0]}_{run_id[1]}'


def print_mail(run_id, track, sensor, dv5, stitch, depsi, dppu):
    print("""Dear radargroup,

A new CAROLINE run has just finished on run {run_id}! 

The characteristics of this run are:
Track(s): {tracks}
Sensor: {sensor}

The following steps were run:
Doris v5: {dv5}
Stitching: {stitch}
Depsi: {depsi}
Depsi-post & portal upload: {dppu}

All CAROLINE results can be accessed at  https://caroline.portal-tud.skygeo.com/portal/caroline/ .

In case of questions, please contact Niels at n.h.jansen@tudelft.nl or Simon at s.a.n.vandiepen@tudelft.nl

Kind regards,
The CAROLINE development team,
Freek, Niels, and Simon""".format(tracks=track,
                                  sensor=sensor,
                                  dv5=dv5,
                                  stitch=stitch,
                                  depsi=depsi,
                                  dppu=dppu,
                                  run_id=run_id))


print_mail(run_id=run_id,
           track=tracks_formatted,
           sensor='Sentinel-1',
           dv5="Yes" if eval(out_parameters['do_doris']) == 1 else "No",
           stitch="Yes" if eval(out_parameters['do_stack_stitching']) == 1 else "No",
           depsi="Yes" if eval(out_parameters['do_depsi']) == 1 else "No",
           dppu="Yes" if eval(out_parameters['do_depsi_post']) == 1 else "No")
