from sys import argv
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name = argv

search_parameters = ['track', 'asc_dsc']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

tracks_formatted = []
for i in range(len(tracks)):
    tracks_formatted.append('{}_t{}'.format(asc_dsc[i], "{:0>3d}".format(tracks[i])))

if len(tracks_formatted) == 1:
    tracks_formatted = tracks_formatted[0]


def print_mail(aoi, track, processing_type, sensor):
    print("""Dear radargroup,

A new DePSI run has just been uploaded into the SkyGeo portal!
Characteristics of the new layer:
AoI: {}
Track(s): {}
Type: {}
Sensor: {}

Viewer: https://caroline.portal-tud.skygeo.com/portal/caroline/

In case of questions, please contact Niels at n.h.jansen@tudelft.nl or Simon at s.a.n.vandiepen@tudelft.nl

Kind regards,
The CAROLINE development team,
Freek, Niels, and Simon
""".format(aoi, track, processing_type, sensor))


print_mail(aoi=AoI_name,
           track=tracks_formatted,
           sensor='Sentinel-1',
           processing_type='PS-DePSI')

