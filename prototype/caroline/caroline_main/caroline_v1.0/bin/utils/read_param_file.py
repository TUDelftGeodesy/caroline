def read_param_file(cpath, param_file, search_parameters):
    """
    Function to read parameters from a parameter file into a dictionary

    :param cpath: directory of the parameter file
    :param param_file: name of the parameter file
    :param search_parameters: list of parameter names to be retrieved
    :return: `dict` with the parameters
    """
    fp = open("{}/{}".format(cpath, param_file))
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
