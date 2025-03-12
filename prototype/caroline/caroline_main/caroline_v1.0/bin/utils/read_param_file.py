def read_param_file(cpath: str, param_file: str, search_parameters: list) -> dict:
    """Read parameters from a parameter file into a dictionary.

    Parameters
    ----------
    cpath : str
        Direcotry of the parameter file
    param_file : str
        Name of the parameter file
    search_parameters: list
        List of parameter names to be retrieved

    Returns
    -------
    dict
        Dictorionary containing the values of the requested parameters. If an invalid parameter is requested,
        `None` is returned for that parameter.
    """
    fp = open(f"{cpath}/{param_file}")
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
            out_parameters[param] = None
            print(f"WARNING: parameter {param} requested but not found in {param_file}. Setting to None")

    return out_parameters
