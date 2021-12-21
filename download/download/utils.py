# '''A library of functions used across modules'''


import fiona
from fiona import collection
import shapely
from shapely.wkt import load, loads
from shapely.geometry import Polygon, MultiPolygon, mapping
import json
import hashlib


import datetime


def convert_date_string(date_string):
    """ Converts data string to a datetime object. 

    Args:
        date_string (sting): date formated as YEAR-MONTH-DAY.

    Returns:
        datetime object
    """
    try:
        datetime_object = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        print('Make sure that start_date is formatted as YEAR-MONTH-DAY')

    return datetime_object


def validate_scihub_download(connector, product, file_path):
    """
    Validates the success of a dowload from the SciHub APIA,
    by performing a data integrity check using checksums.

    Args:
        connector (object): API connector
        product (object): product description including a URI for data download
        file_path (str): path to local copy of the product.
    
    Return: 
        validity chek (bolean)

    """

    #checksum on remote (MD5)
    dowload_uri = product.uri
    checksum_uri = dowload_uri.split('$')[0] + 'Checksum/Value/$value' 
    remote_checksum = connector.get(checksum_uri).text

    local_checksum = compute_checksum(file_path)

    if remote_checksum == local_checksum:
        result = True
    else:
        result = False
    
    return result 


def read_shapefile(file_path):
    """
    Read a .shp file and extracts one or more shapely polygons.

    Args:
        file_path (str): path to shapefile

    Returns:
        List of shapely geometry objects 
    """

    shapes = []
    with collection(file_path, "r") as input_shapefile:
        for shape in input_shapefile:
            # only first shape
            shapes.append(shapely.geometry.shape(shape['geometry']))

    return shapes


def read_kml(file_path):
    """
    Read a .kml file and extracts one or more shapely polygons.

    Args:
        file_path (str): path to KMl file

    Returns:
        List of shapely geometry objects 
    """

    driver = ogr.GetDriverByName('KML')
    dataSource = driver.Open(file_path)
    layer = dataSource.GetLayer()

    shapes = []
    for feature in layer:
        shapes.append(loads(feature.geometry().ExportToWkt()))
    del dataSource, layer

    return shapes


def read_geo_json(geojson):
    """
    Read geojson data from a python dictionary or from a geojson file.

    Args:
        geojson (dic or str): python dictionary (object) or path to json file

    Returns:
        List of shapely geometry objects 
    """

    if isinstance(geojson, str):
        with open(geojson, 'r') as json_file:
            json_data = json.load(json_file)
    else:
        json_data = geojson

    features = json_data["features"]
    shapes = [ shapely.geometry.shape(feature['geometry']) for feature in features ]
    
    return shapes


def read_coordinate_list(coordinates_list):
    """
    Read coordinates from a list to construct a polygon. The list can be formated as a tuple (lat, lon) or
    as two lists [lat-list] [lon-list]

    Args:
        codinates_list (list): 
            1. list of coordinate values pairs of polygon. Each pair should be a tupple (lat, lon), or
            2. list containing two lists of coordinates of a polygon. 
               Each list contains values for lat and lon. Ex. [ [lats], [lons] ]
    Returns:
        A Polygon of type shapely geometry object 
    """

    if not isinstance(coordinates_list, list):
        raise TypeError('Input should be a list of coordinate pairs or a list of latitudes + a list of longitudes.')

    if len(coordinates_list) == 2:
        shapes = Polygon([[lat, lon] for lat, lon in zip(coordinates_list[0], coordinates_list[1])])
    else:
        shapes = Polygon(coordinates_list)

    return shapes


def write_shapefile(shapes, output_file, shape_names=None):
    """
    Write a list of shapely geometry objects into a shapefile.

    Args:
        shapes (list): list of one or more shapely geometry objects
        outpu_file(str): path to the file to be written.
        shape_names(list): an optional list of names to be associated
            with geometry objects.

    """

    schema = {'geometry': 'Polygon', 'properties': {'name': 'str', 'id': 'int'}}

    with fiona.open(output_file, 'w', 'ESRI Shapefile', schema) as shape_dat:
        for id, shape in enumerate(shapes):
            if isinstance(shape_names, list):
                name = shape_names[id]
            else:
                name = str(id)

            shape_dat.write({
                'geometry': mapping(shape),
                'properties': {'id': id, 'name': name},
            })

    return None


def write_kml(shapes, output_file, shape_names=None):
    """
    Write a list of shapely geometry objects into KML file.

    Args:
        shapes (list): list of one or more shapely geometry objects
        outpu_file(str): path to the KML file to be written.
        shape_names(list): an optional list of names to be associated
            with geometry objects.
    """

    driver = ogr.GetDriverByName('KML')
    ds = driver.CreateDataSource(output_file)
    layer = ds.CreateLayer('', None, ogr.wkbPolygon)
    # Add one attribute
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('name', ogr.OFTString))
    defn = layer.GetLayerDefn()

    for id, shape in enumerate(shapes):
        if isinstance(shape_names, list):
            name = shape_names[id]
        else:
            name = str(id)

        # Create a new feature
        feat = ogr.Feature(defn)
        feat.SetField('id', id)
        feat.SetField('name', name)

        # Make a geometry, from Shapely object
        geom = ogr.CreateGeometryFromWkb(shape.wkb)
        feat.SetGeometry(geom)

        layer.CreateFeature(feat)
        feat = geom = None  # destroy these

    # Save and close everything
    ds = layer = feat = geom = None

    return None


def write_geojson(shapes,  outpu_file=None, shape_names=None,):
    """
    Transform shapely geometry objects into a valid GeoJSON.
    if an output_file is passed, a file will be written.

    Args:
        shapes (list): list of one or more shapely geometry objects
        outpu_file(str): optional path to the KML file to be written.
        shape_names(list): an optional list of names to be associated
            with geometry objects.
    
    Returns:
        If a path is passed to 'out_file': a geoJSON.
        If 'output_file = None': a dictionary with vaild JSON. Default.

    """

    feature_collection = {"type": "FeatureCollection",
                            "features": []}

    for id, shape in enumerate(shapes):
        if isinstance(shape_names, list):
            name = shape_names[id]
        else:
            name = str(id)

        json_dict = {"type": "Feature", "properties":{'id': id, 'name': name}, 
                    "geometry":eval(ogr.CreateGeometryFromWkb(shape.wkb).ExportToJson())}
        feature_collection["features"].append(json_dict)

    # writes to file when a path is passed onto output_file
    if isinstance(outpu_file, str):
        with open(outpu_file, 'w') as json_file:
            json.dump(feature_collection, json_file)
    else:
        return feature_collection


def extend_shape(shape, buffer_distance=0.1):
    """
    Create a buffer zone around a Polygon. The result will include the area fo the polygon and the buffer zone.
    
    Args:
        shape (obj): a shapely geometry of a polygon
        buffer_distance (float): distance for the buffer zone. 
            Units depend on the Coordinate System of geometry.

    Returns:
        Polygon of type shapely geometry
    """

    if type(shape) is not Polygon:
        raise TypeError('Geometry is not a Polygon or is not a shapely geometry')

    buffer_zone = shape.buffer(buffer_distance)
    
    return buffer_zone


def simplify_shape(shape, resolution=0.1):
    """
    Simplify the shape of a Polygon. 

    Args:
        shape (obj): a shapely geometry of a polygon
        resolution (float): value to restrict the simplification (tolerance). 
            Resulting coordinates won't be farther from the originals more than the resolution value.
            Units depend on the Coordinate System of geometry.

    """

    if type(shape) is not Polygon:
        raise TypeError('Geometry is not a Polygon or is not a shapely geometry')

    simplified_shape = shape.simplify(resolution)

    return simplified_shape

def compute_checksum(file_path):
    """Computes the MD5 checksume of a file
    Returns:
        Hexadecimal hash
    """

    with open (file_path, 'rb') as local_file:
        file_hash = hashlib.md5()
        while chunk := local_file.read(100*128): # chunk size must be multiple of 128 bytes
            file_hash.update(chunk)
        
    return file_hash.hexdigest()

if __name__ == '__main__':

    import shapely.wkt
    p = shapely.wkt.loads("POLYGON((7.218017578125001 53.27178347923819,7.00927734375 53.45534913802113,6.932373046875 53.72921671251272,6.756591796875 53.68369534495075,6.1962890625 53.57293832648609,5.218505859375 53.50111704294316,4.713134765624999 53.20603255157844,4.5703125 52.80940281068805,4.2626953125 52.288322586002984,3.856201171875 51.88327296443745,3.3508300781249996 51.60437164681676,3.284912109375 51.41291212935532,2.39501953125 51.103521942404186,2.515869140625 50.78510168548186,3.18603515625 50.5064398321055,3.8452148437499996 50.127621728300475,4.493408203125 49.809631563563094,5.361328125 49.475263243037986,6.35009765625 49.36806633482156,6.602783203124999 49.6462914122132,6.536865234375 49.83798245308484,6.251220703125 50.085344397538876,6.448974609375 50.42251884281916,6.218261718749999 50.75035931136963,6.13037109375 51.034485632974125,6.2841796875 51.32374658474385,6.218261718749999 51.59754765771458,6.2841796875 51.754240074033525,6.767578125 51.896833883012484,7.086181640625 52.17393169256849,7.0751953125 52.482780222078226,6.844482421875 52.482780222078226,6.83349609375 52.5897007687178,7.0751953125 52.6030475337285,7.218017578125001 53.27178347923819))")
    pl = [p]
    write_shapefile(pl, '../../data/shape/benelux.shp')