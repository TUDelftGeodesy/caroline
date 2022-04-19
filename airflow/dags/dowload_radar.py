#################################################################################
# DAG for creating Inteferograms using Doris-RIPPL                              #
#################################################################################
# This DAG search, and download radar datasets and orbit files for a time 
# interval, and geographic area. Downloaded datsets are used to produce several 
# products including an interferogram using Doris RIPPL
# 
# Templated fields:
#
# dag_run.conf["start_date"]: 
# dag_run.conf["end_date"]:
# dag_run.conf["geometry"]:
#################################################################################


from datetime import timedelta
from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
# import custom operators
from download_operator import DownloadOperator
from sbatch_operator import SBATCHOperator
# hook to Spider
sshHook = SSHHook(ssh_conn_id='spider_mgarcia') 

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['username@domain.com'],
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
    dag_id='download-data',
    default_args=default_args,
    description='Test DAG download',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'test', 'template'],
) as dag:

    # Commands
    cmd_download_radar ="""
    python main.py conf {{dag_run.conf["start_date"]}} {{dag_run.conf["end_date"]}} --file {{dag_run.conf["geometry"]}} --orbit {{dag_run.conf["orbit_direction"]}}  
    """
    # Other posible paramters.
    # --mode {{dag_run.conf["sensor_mode"]}} --pol {{dag_run.conf["polarisation"]}}

    # Tasks:
    download_radar = DownloadOperator(
    task_id='download_radar_datasets',
    command=cmd_download_radar,
    ssh_hook=sshHook,
    dag=dag)
    

    # dependencies
    download_radar 
