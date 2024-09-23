from sys import argv, path
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, version, caroline_dir = argv

search_parameters = ['sensor', 'polarisation', 'di_finecoreg_mode', 'coregistration_directory',
                     'coregistration_AoI_name', 'track', 'asc_dsc', 'dem_file', 'dem_format', 'dem_size',
                     'dem_upperleft', 'dem_nodata', 'dem_delta']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])
polarisation = eval(out_parameters['polarisation'])
dem_delta = eval(out_parameters['dem_delta'])
dem_size = eval(out_parameters['dem_size'])
dem_upperleft = eval(out_parameters['dem_upperleft'])

for track in range(len(tracks)):
    basedir = "{}/{}_{}_{}_t{:0>3d}/process".format(out_parameters['coregistration_directory'],
                                                    out_parameters['coregistration_AoI_name'],
                                                    out_parameters['sensor'].lower(), asc_dsc[track],
                                                    tracks[track])
    # input files not in need of modification
    for file in ['input.baselines', 'input.coarsecorr', 'input.coarseorb',
                 'input.comprefpha', 'input.coregpm', 'input.finecoreg',
                 'input.mtiming', 'input.reltiming']:
        fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/input_files/{file}", "r")
        data = fr.read()
        fr.close()
        fw = open(f"{basedir}/{file}", "w")
        fw.write(data)
        fw.close()

    for file in ['input.coherence', 'input.interferogram', 'input.resample',
                 'input.subtrrefdem', 'input.subtrrefpha']:
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

    for file in ['input.crop']:
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
                                    pol='')
            fw = open(f"{basedir}/{file}", "w")
            fw.write(data)
            fw.close()
        else:
            for pol in polarisation:
                if pol == 'HH':
                    data = data_base.format(img_name=img_name.format(pol=""),
                                            pol="")
                    fw = open(f"{basedir}/{file}", "w")
                else:
                    data = data_base.format(img_name=img_name.format(pol="_" + pol),
                                            pol="_" + pol)
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
