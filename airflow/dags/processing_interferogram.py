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

from concurrent.futures import process
from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
# import custom operators
from sbatch_operator import SBATCHOperator
# hook to Spider
sshHook = SSHHook(ssh_conn_id='spider_mgarcia') 

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['user@domain.com'],
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
    dag_id='processing-inter',
    default_args=default_args,
    description='Test DAG processing',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'test', 'template'],
) as dag:

    # Commands
    sbatch_body = """
    # load dependencies
    source /project/caroline/Software/bin/init.sh &&
    module load python/3.9.6  gdal/3.4.1 proj/8.2.1
    # Activate virtual environment 
    source /project/caroline/Software/caroline/caroline-venv/bin/activate
    cd /project/caroline/Share/users/caroline-mgarcia
    # path to processing eninge
    PROGRAM="/project/caroline/Software/caroline/processing/processing/interferogram/main.py"
    python $PROGRAM --start_date {{dag_run.conf['start_date']}} --end_date {{dag_run.conf['end_date']}} --process {{dag_run.conf["processes"]}} --name {{dag_run.conf["stack_name"]}} --file {{dag_run.conf["geometry"]}} --resplanar {{dag_run.conf["planar_resolution"]}} --pol {{dag_run.conf["polarisation"]}} -mdate {{dag_run.conf["master_date"]}} || exit 91
    """

    # Tasks:
    create_interferogram = SBATCHOperator(
    task_id='create_interferogram',
    sbatch_commands=sbatch_body,
    script_name="test_processing.sh",
    max_time='59:59',
    frequency = '10s',
    output_dir= "/project/caroline/Share/users/caroline-mgarcia/sbatch",
    cores=2,
    ssh_hook=sshHook,
    dag=dag)
    
    # dependencies
    create_interferogram

