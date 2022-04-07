## Custome Operartor for preparing submiting and monitoring a job using the SBATCH command
## This operator inherits methods and properties of the SSHOperator
## Manuel G. Garcia
## 7-04-2022

from sys import prefix
from time import sleep
from airflow.contrib.operators.ssh_operator import SSHOperator 
from typing import Optional, Sequence, Union
from airflow.exceptions import AirflowException
from airflow.configuration import conf
from base64 import b64encode


def create_sbatch_script(script_file: str, commands:str, max_time:str, cores=1, tasks=1,  nodes=1, partition='normal', qos='long')-> None:
    """
    Creates a bash script describing a Slurm job for Spider.

    Args:
        script_file: path and name for the sbash script with .sh extension.
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
    echo "Starting time:"; date
    {commands}
    echo "Finished at:"; date
    """

    # return  header + body
    with open(f'{script_file}', 'w') as script_file:
        script_file.write(header)
        script_file.write(body)
    
    return None


class SBATCHOperator(SSHOperator):
    def __init__(self, sbatch_commands: str, script_file: str, max_time:str, frequency="1m", job_output=None,  cores=1, tasks=1,  nodes=1, partition='normal', qos='long', **kwargs) -> None:
        """Submits a job using an sbacth script to Spider. The job status is monitored until complete or failure.
           Inherits properties and methods from the SSHOperator.
           Requires an SSHHook.
        Args:
            sbatch_command (str): commands for the body of the sbatch script.
            script_file (str): path and name for the sbash script.
            max_time (str): maximum run time for the slurm job, [HH:MM:SS] or [MM:SS] or [minutes]
            frequency (str): time interval at which the status of a job will be checked. Default is 1 minute.
            job_output (str): path to directory for the slurm output file. If None, output file will be in
                home directory.
            cores: number of cores to request to the cluster.
            tasks: number of tasks to request to the cluster.
            nodes: number of node to request to the cluster.
            partition: partition type.
            qos: quality of service to request to the cluster.
        """
    
        super().__init__(**kwargs) # inherit properties from parent class
        self.commands = sbatch_commands 
        self.monitoring_frequency  = frequency
        self.job_output = job_output
        self.script_file = script_file
        self.max_time = max_time
        self.cores = cores
        self.tasks = tasks
        self.nodes = nodes
        self.partition = partition
        self.qos = qos

    def execute(self, context=None) -> Union[bytes, str]:
        result: Union[bytes, str]
        if self.commands is None:
            raise AirflowException("SBATCH operator error: command for the body of script not specified. Aborting.")

        # Set default directory for slurm output files
        if self.job_output is None:
            self.job_output = "~/"

        # Forcing get_pty to True if the command begins with "sudo".
        self.get_pty = self.commands.startswith('sudo') or self.get_pty

        # prepare sbatch script
        create_sbatch_script(script_file=self.script_file, 
                            commands=self.commands, 
                            max_time=self.max_time, 
                            cores=self.cores, 
                            tasks=self.tasks, 
                            nodes=self.nodes, 
                            partition=self.partition, 
                            qos=self.qos
                            )

        submit_job= f"""
        cd {self.job_output}
        JID=$(sbatch {self.script_file})
        echo  $JID
        sleep 10s 
        """

        monitoring = f"""
        ST="PENDING"
        while [ "$ST" != "COMPLETED" ]
        do
            ST=$(sacct -j ${{JID##* }} -o State | awk 'FNR == 3 {{print $1}}')
            sleep {self.monitoring_frequency}
             if [ "$ST" == "FAILED" ]
            then
                echo 'Job final status:' $ST, exiting...
                exit 122
            fi
        done
        echo $ST
        """
        command = submit_job + monitoring

        try:
            with self.get_ssh_client() as ssh_client:
                result = self.run_ssh_client_command(ssh_client, command)
        except Exception as e:
            raise AirflowException(f"SBATCH operator error: {str(e)}")

        enable_pickling = conf.getboolean('core', 'enable_xcom_pickling')
        if not enable_pickling:
            result = b64encode(result).decode('utf-8')
        return result
