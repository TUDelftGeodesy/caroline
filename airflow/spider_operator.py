# from airflow.contrib.hooks.ssh_hook import SSHHook
from click import command
from airflow.models.baseopertor import BaseOperator
from airflow.contrib.operators.ssh_operator import SSHOperator 
from typing import TYPE_CHECKING, Optional, Sequence, Union
from airflow.exceptions import AirflowException
from airflow.configuration import conf
from base64 import b64encode

class SpiderSSHOperator(SSHOperator):
    def __init__(self, s_command: str, **kwargs) -> None:
        
        super().__init__(**kwargs) # inherit properties from parent class

        self.s_command = s_command # command to be appended 


## from ssh operator
    # def execute(self, context=None) -> Union[bytes, str]:
    #     result: Union[bytes, str]
    #     if self.command is None:
    #         raise AirflowException("SSH operator error: SSH command not specified. Aborting.")

    #     # Forcing get_pty to True if the command begins with "sudo".
    #     self.get_pty = self.command.startswith('sudo') or self.get_pty

    #     try:
    #         with self.get_ssh_client() as ssh_client:
    #             result = self.run_ssh_client_command(ssh_client, self.command)
    #     except Exception as e:
    #         raise AirflowException(f"SSH operator error: {str(e)}")
    #     enable_pickling = conf.getboolean('core', 'enable_xcom_pickling')
    #     if not enable_pickling:
    #         result = b64encode(result).decode('utf-8')
    #     return result


    def execute(self, context=None) -> Union[bytes, str]:
        result: Union[bytes, str]
        if self.command is None:
            raise AirflowException("SSH operator error: SSH command not specified. Aborting.")

        # Forcing get_pty to True if the command begins with "sudo".
        self.get_pty = self.command.startswith('sudo') or self.get_pty
        
        # load modules and activate virtual environments
        prefix = """
            source /project/caroline/Software/bin/init.sh &&
            source /project/caroline/Software/download/python-gdal/bin/activate &&
            cd /project/caroline/Software/caroline/download/download/ &&
            module load python/3.9.6  gdal/3.4.1 &&
            """

        command = prefix + self.s_command

        try:
            with self.get_ssh_client() as ssh_client:
                result = self.run_ssh_client_command(ssh_client, command)
        except Exception as e:
            raise AirflowException(f"SSH operator error: {str(e)}")

        enable_pickling = conf.getboolean('core', 'enable_xcom_pickling')
        if not enable_pickling:
            result = b64encode(result).decode('utf-8')
        return result


