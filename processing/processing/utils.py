"""
A library of functions used accross modules
"""

from turtle import st
import shapely.wkt

def list_of_data_type(_input:list, data_type=str) -> bool:
    """Check if input is a list of items of type 'data_type'
    Args:
        _input (list): list to be tested
        data_type: the python datatype that items in the list must be
    Returns true if inputs is a list of strings
    """
    if not isinstance(_input, list):
        raise TypeError("Input is not a list")
        
    if len(_input) <= 0:
        raise TypeError("Empty list")

    result = True
    for item in _input:
        test = isinstance(item, data_type)
        result = result and test

    return result

def wkt_to_list(wkt:str) -> list:
    """Converts well-know-text polygon to Doris-Rippl list of coordinates polygon representation
    Args:
        wkt (str):  polygon as well know text.
    Returns:
        A nested list of coordinate pairs, such as [[x1,y1], [x2,y2]] 
    """

    polygon = shapely.wkt.loads(wkt)
    wkt_coords = polygon.exterior.coords
    coords_list = []
    
    for coord in wkt_coords:
        # srtip coordinate pairs (tupples) and construct list of lists
        coords_list.append( [coord[0], coord[1]] )

    return coords_list

