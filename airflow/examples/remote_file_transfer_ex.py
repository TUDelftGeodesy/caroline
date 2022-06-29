#################################################################################
# File Tansfer Example                                                     #
#################################################################################
# This example shows how to use the transfer files between Spider 
# and the Aiflow VM in a DAG using Jinja templates
# for command parameters.
# directory at the airflow root directory.
# A sshHook to Spider is required.
#
#
# Running the DAG:
# =================
# Values for templated parameters must be passed as Json.
# E.g.
# {"stack_name":"test_stack" }
#################################################################################

from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.utils.dates import days_ago
# import custom operator
from download_operator import DownloadOperator
# hook to spider.surfsara.nl
sshHook = SSHHook(ssh_conn_id='spider_mgarcia')

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['m.g.garciaalvarez@tudelft.nl'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue', 
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

with DAG(
    dag_id='file-transfer',
    default_args=default_args,
    description='Test remote file transfer with SCP',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'example'],
) as dag:

    cmd_file_compression="""
    zip -r /project/caroline/Share/users/caroline-mgarcia/products/sentinel1/{{dag_run.conf["stack_name"]}}/interferogram.zip /project/caroline/Share/users/caroline-mgarcia/products/sentinel1/{{dag_run.conf["stack_name"]}}/interferogram 
    """

    # WARNING: -o StrictHostKeyChecking=no will automatically accepts connections from any host. 
    # This reduces security. Ideally host verification is handled in a different way.
    cmd_transfer_file ="""
    scp -i /opt/airflow/ssh/caroline_rsa -o StrictHostKeyChecking=no caroline-mgarcia@spider.surfsara.nl:/project/caroline/Share/users/caroline-mgarcia/products/sentinel1/{{dag_run.conf["stack_name"]}}/interferogram.zip /opt/airflow/data/temp/interf-{{dag_run.conf["stack_name"]}}.zip
    """

    # Prevents piling up data by deleting the zip file created by 'file compression'
    cmd_clean_up="""
    rm /project/caroline/Share/users/caroline-mgarcia/products/sentinel1/{{dag_run.conf["stack_name"]}}/interferogram.zip
    """
    
    compress_file = SSHOperator(
    task_id='compress_output',
    command=cmd_file_compression,
    ssh_hook=sshHook,
    dag=dag
    )

    transfer_file = BashOperator(
    task_id='transfer_file',
    bash_command=cmd_transfer_file,
    dag=dag
    )

    clean_up = SSHOperator(
    task_id='clean_up',
    command=cmd_clean_up,
    ssh_hook=sshHook,
    dag=dag
    )
    
    # dependencies
    compress_file >> transfer_file >> clean_up
