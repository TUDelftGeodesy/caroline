from sys import argv, path
import os
import fiona
import numpy as np
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, version, caroline_dir = argv

search_parameters = ['sensor', 'polarisation', 'di_finecoreg_mode', 'coregistration_directory',
                     'coregistration_AoI_name', 'track', 'asc_dsc', 'dem_file', 'dem_format', 'dem_size',
                     'dem_upperleft', 'dem_nodata', 'dem_delta', 'shape_directory', 'shape_AoI_name']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])
polarisation = eval(out_parameters['polarisation'])
dem_delta = eval(out_parameters['dem_delta'])
dem_size = eval(out_parameters['dem_size'])
dem_upperleft = eval(out_parameters['dem_upperleft'])


def get_pixelsize(sensor):
    # returns pixel size in m
    if sensor == 'TSX':
        d_az = 3
        d_r = 3
    elif sensor == 'RSAT2':
        d_az = 11.8
        d_r = 8
    elif sensor == 'ERS':
        d_az = 8
        d_r = 4
    elif sensor == 'ENV':
        d_az = 30
        d_r = 30
    elif sensor == 'Cosmo':
        d_az = 15
        d_r = 15
    elif sensor == 'PAZ':
        d_az = 3
        d_r = 3
    elif sensor == 'ALOS2':
        d_az = 10
        d_r = 10
    elif sensor == 'TDX':
        d_az = 3
        d_r = 3
    else:
        raise ValueError(f'Unknown sensor {sensor}!')
    return d_az, d_r


def haversine(lat1, lat2, lon1, lon2):  # calculates the distance between two points on a sphere
    dphi = np.radians(lat1 - lat2)
    dlambda = np.radians(lon1 - lon2)
    R = 6378136  # m, radius of Earth
    dist = 2 * R * np.arcsin(np.sqrt((1 - np.cos(dphi) + np.cos(np.radians(lat1)) *
                                      np.cos(np.radians(lat2)) * (1 - np.cos(dlambda))) / 2))
    return dist


shapefile = out_parameters['shape_directory'] + '/' + out_parameters['shape_AoI_name'] + '_shape.shp'

shape = fiona.open(shapefile)
shape_iter = iter(shape)
finished = False
polys = []
while not finished:
    try:
        shp = next(shape_iter)
        poly = shp['geometry']['coordinates']
        for pol in poly:
            polys.append(pol)
    except StopIteration:
        finished = True

assert len(polys) == 1, "Found more than one AoI polygon! Aborting..."

poly = np.array(polys[0])
min_lat = min(poly[:, 1])
max_lat = max(poly[:, 1])
min_lon = min(poly[:, 0])
max_lon = max(poly[:, 0])
center_lon = (max_lon + min_lon) / 2
center_lat = (max_lat + min_lat) / 2

if min_lat < 0:
    if max_lat > 0:
        ref_lat = 0
    else:
        ref_lat = max_lat
else:
    ref_lat = min_lat

dist_lat = haversine(min_lat, max_lat, min_lon, min_lon)
dist_lon = haversine(ref_lat, ref_lat, min_lon, max_lon)  # calculated at the widest part of the AoI

d_az, d_r = get_pixelsize(out_parameters['sensor'])
pix_dr = int(np.ceil(dist_lon / d_r * 1.05))
pix_daz = int(np.ceil(dist_lat / d_az * 1.05))

for track in range(len(tracks)):
    basedir = "{}/{}_{}_{}_t{:0>3d}/process".format(out_parameters['coregistration_directory'],
                                                    out_parameters['coregistration_AoI_name'],
                                                    out_parameters['sensor'].lower(), asc_dsc[track],
                                                    tracks[track])
    # input files not in need of modification
    for file in ['input.baselines', 'input.coarsecorr', 'input.coarseorb',
                 'input.comprefpha', 'input.coregpm',
                 'input.mtiming', 'input.reltiming']:
        fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/input_files/{file}", "r")
        data = fr.read()
        fr.close()
        fw = open(f"{basedir}/{file}", "w")
        fw.write(data)
        fw.close()

    for file in ['input.coherence', 'input.interferogram', 'input.subtrrefdem', 'input.subtrrefpha']:
        fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/input_files/{file}", "r")
        data_base = fr.read()
        fr.close()
        for pol in polarisation:
            if pol == 'HH':
                data = data_base.format(pol="")
                fw = open(f"{basedir}/{file}", "w")
            else:
                data = data_base.format(pol="_"+pol)
                fw = open(f"{basedir}/{file}_{pol}", "w")
            fw.write(data)
            fw.close()

    for file in ['input.resample']:
        fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/input_files/{file}", "r")
        data_base = fr.read()
        fr.close()
        for pol in polarisation:
            if pol == 'HH':
                data = data_base.format(pol="",
                                        center_lat=center_lat,
                                        center_lon=center_lon,
                                        pix_az=pix_daz,
                                        pix_r=pix_dr)
                fw = open(f"{basedir}/{file}", "w")
            else:
                data = data_base.format(pol="_"+pol,
                                        center_lat=center_lat,
                                        center_lon=center_lon,
                                        pix_az=pix_daz,
                                        pix_r=pix_dr)
                fw = open(f"{basedir}/{file}_{pol}", "w")
            fw.write(data)
            fw.close()

    for file in ['input.crop']:
        # pixels + 500 to eliminate edge effects
        # needs polarisation only for RSAT2
        if out_parameters['sensor'] == 'ALOS2':
            img_name = 'IMG.1'
        elif out_parameters['sensor'] == 'Cosmo':
            img_name = 'image.h5'
        elif out_parameters['sensor'] == 'ENV':
            img_name = 'image.N1'
        elif out_parameters['sensor'] == 'ERS':
            img_name = 'DAT_01.001'
        elif out_parameters['sensor'] == 'RSAT2':
            img_name = 'imagery{pol}.tif'
            # loop over polarisations to get additional crop files
        elif out_parameters['sensor'] == 'TSX':
            img_name = 'image.cos'
        else:
            raise ValueError(f'Unknown sensor {out_parameters["sensor"]}!')

        fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/input_files/{file}", "r")
        data_base = fr.read()
        fr.close()

        if out_parameters['sensor'] != 'RSAT2':
            data = data_base.format(img_name=img_name,
                                    pol='',
                                    center_lat=center_lat,
                                    center_lon=center_lon,
                                    pix_az=pix_daz+500,
                                    pix_r=pix_dr+500)
            fw = open(f"{basedir}/{file}", "w")
            fw.write(data)
            fw.close()
        else:
            for pol in polarisation:
                if pol == 'HH':
                    data = data_base.format(img_name=img_name.format(pol=""),
                                            pol="",
                                            center_lat=center_lat,
                                            center_lon=center_lon,
                                            pix_az=pix_daz + 500,
                                            pix_r=pix_dr + 500)
                    fw = open(f"{basedir}/{file}", "w")
                else:
                    data = data_base.format(img_name=img_name.format(pol="_" + pol),
                                            pol="_" + pol,
                                            center_lat=center_lat,
                                            center_lon=center_lon,
                                            pix_az=pix_daz + 500,
                                            pix_r=pix_dr + 500)
                    fw = open(f"{basedir}/{file}_{pol}", "w")
                fw.write(data)
                fw.close()

    for file in ['input.comprefdem', 'input.dembased', 'input.simamp']:
        fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/input_files/{file}", "r")
        data_base = fr.read()
        data = data_base.format(dem_file=out_parameters['dem_file'],
                                dem_format=out_parameters['dem_format'],
                                dem_s1=dem_size[0],
                                dem_s2=dem_size[1],
                                dem_d1=dem_delta[0],
                                dem_d2=dem_delta[1],
                                dem_ul1=dem_upperleft[0],
                                dem_ul2=dem_upperleft[1],
                                dem_nodata=out_parameters['dem_nodata'])
        fr.close()
        fw = open(f"{basedir}/{file}", "w")
        fw.write(data)
        fw.close()

    for file in ['input.finecoreg']:
        if out_parameters['di_finecoreg_mode'] == 'simple':
            appendix = '_simple'
            nwin = 5000
        elif out_parameters['di_finecoreg_mode'] == 'normal':
            appendix = ''
            nwin = 8000
        else:
            raise ValueError(f'Unknown finecoreg_mode {out_parameters["di_finecoreg_mode"]}!')
        fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/input_files/{file}", "r")
        data_base = fr.read()
        fr.close()
        data = data_base.format(nwin=nwin)
        fw = open(f"{basedir}/{file}{appendix}", "w")
        fw.write(data)
        fw.close()

    for file in ['input.porbit']:
        # only necessary for ERS and ENV
        fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/input_files/{file}", "r")
        data_base = fr.read()
        fr.close()
        if out_parameters['sensor'] == 'ERS':
            for directory in ['ERS1', 'ERS2']:  # needs both
                data = data_base.format(directory=directory)
                fw = open(f"{basedir}/{file}_{directory}", "w")
                fw.write(data)
                fw.close()
        elif out_parameters['sensor'] == 'ENV':
            directory = 'envisat/dor_vor_odr'
            data = data_base.format(directory=directory)
            fw = open(f"{basedir}/{file}", "w")
            fw.write(data)
            fw.close()

    for file in ['input.readfiles']:
        if out_parameters['sensor'] == 'ALOS2':
            method = 'ALOS2'
            dat = 'IMG.1'
            lea = 'LED.1'
            vol = 'VOL.1'
            order = ['method', 'dat', 'lea', 'vol']
        elif out_parameters['sensor'] == 'Cosmo':
            method = 'CSK'
            dat = 'image.h5'
            order = ['method', 'dat']
        elif out_parameters['sensor'] == 'ERS':
            method = 'ERS'
            vol = 'VDR_DAT.001'
            dat = 'DAT_01.001'
            lea = 'LEA_01.001'
            null = 'dummy'
            order = ['method', 'vol', 'dat', 'lea', 'null']
        elif out_parameters['sensor'] == 'ENV':
            method = 'ASAR'
            dat = 'image.N1'
            order = ['method', 'dat']
        elif out_parameters['sensor'] == 'RSAT':
            method = 'RSAT'
            vol = 'VDF_DAT.001'
            dat = 'DAT_01.001'
            lea = 'LEA_01.001'
            null = 'dummy'
            order = ['method', 'vol', 'dat', 'lea', 'null']
        elif out_parameters['sensor'] == 'RSAT2':
            method = 'RADARSAT-2'
            dat = 'imagery_HH.tif'
            lea = 'product.xml'
            order = ['method', 'dat', 'lea']
        elif out_parameters['sensor'] == 'TSX':
            method = 'TSX'
            dat = 'image.cos'
            lea = 'leader.xml'
            order = ['method', 'dat', 'lea']
        else:
            raise ValueError(f'Unknown sensor {out_parameters["sensor"]}!')
        strng = ''
        for param in order:
            line = "{: <16s}{}\n".format("S_IN_{}".format(param.upper()), eval(param))
            strng += line
        strng = strng[:-1]  # cut off the last \n

        fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/input_files/{file}", "r")
        data_base = fr.read()
        fr.close()
        data = data_base.format(data_string=strng)
        fw = open(f"{basedir}/{file}", "w")
        fw.write(data)
        fw.close()
