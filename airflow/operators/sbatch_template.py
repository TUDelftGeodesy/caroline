

def create_sbatch_script(script_file: str, commands:str, cores:int, tasks:int, max_time:str, nodes=1, partition='normal', qos='long')-> None:
    """
    Creates a bash script describing a Slurm job for Spider.

    Args:
        script_file: path and name for the sbash script.
        commands: bash commands to be for the body of the sbash script.
        cores: number of cores to request to the cluster.
        tasks: number of tasks to request to the cluster.
        max_time: maximum run time in [HH:MM:SS] or [MM:SS] or [minutes]
        nodes: number of node to request to the cluster.
        partition: partition type.
        qos: quality of service to request to the cluster.
    """
    header = f"""
    #!/bin/bash\n
    #SBATCH -N {nodes}			# number of nodes
    #SBATCH -c {cores}			# number of cores; coupled to 8000 MB memory per core
    #SBATCH -t {max_time}		# maximum run time in [HH:MM:SS] or [MM:SS] or [minutes]
    #SBATCH -p {partition}		# partition (queue); job can run up to 5 days
    #SBATCH --qos={qos}		
    #SBATCH --ntasks={tasks}
    """

    body = f"""
    echo "Starting time:"; date \n
    {commands} \n
    echo "Finished at:"; date
    """

    # return  header + body
    with open(f'{script_file}.sh', 'w') as script_file:
        script_file.write(header)
        script_file.write(body)
    
    return None
