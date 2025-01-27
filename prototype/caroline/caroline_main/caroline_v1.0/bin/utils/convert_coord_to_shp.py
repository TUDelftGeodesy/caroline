from sys import argv
from read_param_file import read_param_file

filename, param_file, cpath, AoIname = argv  # crop_length = Delta latitude in km, crop_width = Delta longitude in km

search_parameters = ['center_AoI', 'AoI_width', 'AoI_length', 'shape_directory', 'shape_file']
out_parameters = read_param_file(cpath, param_file, search_parameters)

if out_parameters['shape_file'] is None:  # backwards compatibility, shape_file path is not present
    out_parameters['shape_file'] = ''  # empty shape_file path to lead to square AOI generation

central_coord = eval(out_parameters['center_AoI'])
crop_length = eval(out_parameters['AoI_length'])
crop_width = eval(out_parameters['AoI_width'])
export_shp = "{}/{}_shape.shp".format(out_parameters['shape_directory'], AoIname)

if len(out_parameters['shape_file']) != 0:  # shape file is given
    if out_parameters['shape_file'][-4:] != '.shp':
       raise ValueError("Given shapefile does not end in .shp!")
    import os
    for appendix in ["shp", "prj", "shx", "dbf"]:
        os.system('ln -s {}.{} {}.{}'.format(out_parameters['shape_file'][:-4], appendix, export_shp[:-4], appendix))

else:  # generate a square shapefile around the center coordinate
    import osgeo
    from osgeo import ogr, osr
    from math import sin, cos, pi, radians

    R = 6378136  # m

    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromEPSG(4326)  # WGS84
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapeData = driver.CreateDataSource(export_shp) 
    layer = shapeData.CreateLayer('layer', spatialReference, ogr.wkbPolygon)
    layer_defn = layer.GetLayerDefn()

    Dlat_m = 2*pi*R/360  # m per degree of latitude

    N_limit = central_coord[0]+crop_length*1000/2/Dlat_m
    S_limit = central_coord[0]-crop_length*1000/2/Dlat_m

    W_limit = min(central_coord[1]-crop_width*1000/2/(Dlat_m*cos(radians(N_limit))),
                  central_coord[1]-crop_width*1000/2/(Dlat_m*cos(radians(S_limit))))
    E_limit = max(central_coord[1]+crop_width*1000/2/(Dlat_m*cos(radians(N_limit))),
                  central_coord[1]+crop_width*1000/2/(Dlat_m*cos(radians(S_limit))))

    print(N_limit,S_limit,W_limit,E_limit)

    coords = [[N_limit, W_limit], [N_limit, E_limit], [S_limit, E_limit], [S_limit, W_limit], [N_limit, W_limit]]

    index = 0

    lines = ogr.Geometry(ogr.wkbLinearRing)

    for coord in coords:
        lines.AddPoint(coord[1], coord[0])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(lines)
    feature = ogr.Feature(layer_defn)
    feature.SetGeometry(poly)
    feature.SetFID(index)
    layer.CreateFeature(feature)

    shapeData.Destroy()
