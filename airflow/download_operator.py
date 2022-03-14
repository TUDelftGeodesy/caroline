## Custome Operartor for using the Download Engine in the Spider HPC
## This operator inherits methods and properties of the SSHOperator
## Manuel G. Garcia
## 14-03-2022

from airflow.contrib.operators.ssh_operator import SSHOperator 
from typing import Optional, Sequence, Union
from airflow.exceptions import AirflowException
from airflow.configuration import conf
from base64 import b64encode

class DownloadOperator(SSHOperator):
    def __init__(self, command: str, **kwargs) -> None:
        """Activies virtual environment and loads modules for the Download Engine.
           Inherits properties and methods from the SSHOperator
        Args:
            command (str): command to be executed after modules and environment are loaded.
            """
    
        super().__init__(**kwargs) # inherit properties from parent class
        self.command = command # command to be appended 

    def execute(self, context=None) -> Union[bytes, str]:
        result: Union[bytes, str]
        if self.command is None:
            raise AirflowException("SSH operator error: SSH command not specified. Aborting.")

        # Forcing get_pty to True if the command begins with "sudo".
        self.get_pty = self.command.startswith('sudo') or self.get_pty
        
        # Python environment and modules required by for donwload engine
        prefix = """
            source /project/caroline/Software/bin/init.sh &&
            source /project/caroline/Software/download/python-gdal/bin/activate &&
            cd /project/caroline/Software/caroline/download/download/ &&
            module load python/3.9.6  gdal/3.4.1 &&
            """

        command = prefix + self.command

        try:
            with self.get_ssh_client() as ssh_client:
                result = self.run_ssh_client_command(ssh_client, command)
        except Exception as e:
            raise AirflowException(f"SSH operator error: {str(e)}")

        enable_pickling = conf.getboolean('core', 'enable_xcom_pickling')
        if not enable_pickling:
            result = b64encode(result).decode('utf-8')
        return result
