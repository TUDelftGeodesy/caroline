"""
A library of functions used accross modules
"""

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