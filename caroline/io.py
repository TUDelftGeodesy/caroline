import os


def read_parameter_file(parameter_file: str, search_parameters: list) -> dict:
    """Read parameters from a CAROLINE parameter file into a dictionary.

    Parameters
    ----------
    parameter_file : str
        Absolute path to the CAROLINE parameter file in .txt format
    search_parameters: list
        Parameter names to be retrieved from the parameter file, as a list of strings

    Returns
    -------
    dict
        Dictionary containing the values of the requested parameters. If an invalid parameter is requested,
        `None` is returned for that parameter.

    Raises
    ------
    AssertionError
        - When the parameter file does not exist
        - When the parameter file does not end in .txt

    ValueError
        - When a requested parameter does not exist in the parameter file
    """
    assert os.path.exists(parameter_file), f"Specified parameter file {parameter_file} does not exist!"
    assert parameter_file.split(".")[-1] == "txt", f"Specified parameter file {parameter_file} is not a .txt file!"

    fp = open(parameter_file)
    parameters = fp.read().split("\n")
    fp.close()

    out_parameters = {}

    for param in search_parameters:
        found = False
        for p in parameters:
            if p.split("=")[0].strip() == param:
                do = p.split("=")[1]
                if "#" in do:
                    do = do.split("#")[0]
                do = do.strip().strip("'").strip('"')
                out_parameters[param] = do
                found = True
                break
        if not found:
            raise ValueError(f"Parameter {param} requested but not in {parameter_file}!")

    return out_parameters
