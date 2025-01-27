from sys import argv
filename, param_file, cpath, AoIname = argv  # crop_length = Delta latitude in km, crop_width = Delta longitude in km

pf = open("{}/{}".format(cpath, param_file))
parameters = pf.read().split("\n")
pf.close()

search_parameters = ['center_AoI', 'AoI_width', 'AoI_length','shape_directory']
out_parameters = []

for param in search_parameters:
    for p in parameters:
	if param in p:
	    do = p.split("=")[1]
	    if "#" in do:
		do = do.split("#")[0]
	    do = do.strip().strip('"').strip("'")
	    out_parameters.append(do)
	    break


central_coord = eval(out_parameters[0])
crop_length = eval(out_parameters[2])
crop_width = eval(out_parameters[1])
export_shp = "{}/{}_shape.shp".format(out_parameters[3], AoIname)


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
    #point = ogr.Geometry(ogr.wkbPoint)
    lines.AddPoint(coord[1], coord[0])
    #feature = ogr.Feature(layer_defn)
    #feature.SetGeometry(point)
    #feature.SetFID(index)
    #layer.CreateFeature(feature)

poly = ogr.Geometry(ogr.wkbPolygon)
poly.AddGeometry(lines)
feature = ogr.Feature(layer_defn)
feature.SetGeometry(poly)
feature.SetFID(index)
layer.CreateFeature(feature)

shapeData.Destroy()



