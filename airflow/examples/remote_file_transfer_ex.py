#################################################################################
# File Transfer Example                                                     #
#################################################################################
# This example shows how to transfer files from Spider
# to the Aiflow VM using SCP.
# A sshHook to Spider is required.
#
# TEMPLATED PARAMETERS:
# stack_name

# Running the DAG:
# =================
# Values for templated parameters must be passed as Json.
# E.g.
# {"stack_name": "demo_stack"}
#################################################################################

from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.utils.dates import days_ago
# hook to spider.surfsara.nl
sshHook = SSHHook(ssh_conn_id='spider_mgarcia')

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['net_id@tudelft.nl'],
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
    # This reduce security. Ideally host verification is handled in a different way.
    cmd_transfer_file ="""
    scp -i /opt/airflow/ssh/caroline_rsa -o StrictHostKeyChecking=no caroline-mgarcia@spider.surfsara.nl:/project/caroline/Share/users/caroline-mgarcia/products/sentinel1/{{dag_run.conf["stack_name"]}}/interferogram.zip /opt/airflow/data/interf-{{dag_run.conf["stack_name"]}}.zip
    """

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

    # Delete compressed files from Spider
    clean_up = SSHOperator(
    task_id='clean_up',
    command=cmd_clean_up,
    ssh_hook=sshHook,
    dag=dag
    )
    
    # dependencies
    compress_file >> transfer_file >> clean_up
