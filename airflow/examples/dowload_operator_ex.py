#################################################################################
# Download Operator Example                                                     #
#################################################################################
# This example shows how to use the custom DownloadOperator
# in a DAG using Jinja templates for command parameters. 
# We assume that the operator is available via the plugings
# directory at the airflow root directory.
# A sshHook to an instance of Slurm is required.
#
# The DowloadOperator inherits from the SSHOperator and
# loads Spider depependencies before executing Python
# commands on Download Engine.
# To this end, the SSHOperator was extended with the 
# following arguments:
#   command (str): command to be executed after modules and 
#       environment are loaded.
#
# Running the DAG:
# =================
# Values for templated parameters must be passed as Json.
# E.g.
# {"start_date":"2021-12-19", 
# "end_date":"2021-12-22", 
# "geometry":"POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))"}
#################################################################################

from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
# import custom operator
from download_operator import DownloadOperator
# hook to Spider
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
    dag_id='dowload-operator',
    default_args=default_args,
    description='Test DAG download',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'example'],
) as dag:

    # PARAMETERS
    # dag_run.conf["start_date"]
    # dag_run.conf["end_date"]
    # dag_run.conf["geometry"]

    # command for Download Engine
    cmd_download_radar ="""
    python engine.py conf '{{dag_run.conf["start_date"]}}' '{{dag_run.conf["end_date"]}}' -a '{{dag_run.conf["geometry"]}}'
    """

    # task with DownloadOperator
    download_radar = DownloadOperator(
    task_id='download_radar',
    command=cmd_download_radar,
    ssh_hook=sshHook,
    dag=dag)
    
    # dependencies
    download_radar 
