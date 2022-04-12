## Custome Operartor for monitoring a Slurm Job in the Spider HPC
## This operator inherits methods and properties of the SSHOperator
## Manuel G. Garcia
## 14-03-2022

from sys import prefix
from time import sleep
from airflow.contrib.operators.ssh_operator import SSHOperator 
from typing import Optional, Sequence, Union
from airflow.exceptions import AirflowException
from airflow.configuration import conf
from base64 import b64encode

class SlurmOperator(SSHOperator):
    def __init__(self, command: str, monitor_time="1m", output_file=None, **kwargs) -> None:
        """Submits a job using sbacth to Spider. The job statatus is monitored until completed or failed.
           Inherits properties and methods from the SSHOperator.
           Requires an SSHHook.
        Args:
            sbatch_command (str): command to submit a slurm script. E.g., sbatch <path to script.sh>
            monitor_time (str): time interval at which the status of a job will be checked. Default is 1 minute.
            output_file (str): path to directory for the slurm output file. If None, output file will be in
                         home directory.
        """
    
        super().__init__(**kwargs) # inherit properties from parent class
        self.command = command 
        self.monitor_time  = monitor_time
        self.output_file = output_file

    def execute(self, context=None) -> Union[bytes, str]:
        result: Union[bytes, str]
        if self.command is None:
            raise AirflowException("SSH operator error: SSH command not specified. Aborting.")

        # Set default directory for slurm output files
        if self.output_file is None:
            self.output_file = "~/"

        # Forcing get_pty to True if the command begins with "sudo".
        self.get_pty = self.command.startswith('sudo') or self.get_pty
        
        submit ="""
        cd """ + self.output_file + """
        JID=$(""" + self.command + """)
        echo  $JID
        sleep 10s 
        """

        monitor = """
        ST="PENDING"
        while [ "$ST" != "COMPLETED" ]
        do
            ST=$(sacct -j ${JID##* } -o State | awk 'FNR == 3 {print $1}')
            sleep """ + self.monitor_time + """
            if [ "$ST" == "FAILED" ]
            then
                echo 'Job final status:' $ST, exiting...
                exit 122
            fi
        done
        echo $ST
        """
        
        command = submit + monitor

        try:
            with self.get_ssh_client() as ssh_client:
                result = self.run_ssh_client_command(ssh_client, command)
        except Exception as e:
            raise AirflowException(f"SSH operator error: {str(e)}")

        enable_pickling = conf.getboolean('core', 'enable_xcom_pickling')
        if not enable_pickling:
            result = b64encode(result).decode('utf-8')
        return result
