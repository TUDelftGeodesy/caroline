# A DAG for the creation of inteferograms on Spider 
from datetime import timedelta, datetime

import airflow
from airflow import DAG
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
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
    dag_id='interferogram',
    default_args=default_args,
    description='Test DAG download',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline'],
) as dag:

    # Bash commands
    cmd_download_radar ="""
    source /project/caroline/Software/bin/init.sh &&
    source /project/caroline/Software/download/venv39/bin/activate &&
    cd /project/caroline/Software/caroline/download/download/ &&
    module load python/3.9.6 &&
    python engine.py conf '2021-12-19' '2021-12-22' -a 
    'POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))'
    """

    cmd_download_orbits ="""
    source /project/caroline/Software/bin/init.sh &&
    source /project/caroline/Software/download/venv39/bin/activate &&
    cd /project/caroline/Software/caroline/download/download/ &&
    module load python/3.9.6 &&
    python orbits.py conf '2021-12-19' '2021-12-22'
    """

    cmd_processing="""
    source /project/caroline/Software/bin/init.sh &&
    source /project/caroline/Software/download/venv39/bin/activate &&
    cd /project/caroline/Software/caroline/download/download/ &&
    module load python/3.9.6 
    # call DORIS-RIPPL
    """

    download_radar = SSHOperator(
    task_id='download_radar',
    command=cmd_download_radar,
    ssh_hook=sshHook,
    dag=dag)

    download_orbits = SSHOperator(
    task_id='download_orbits',
    command=cmd_download_orbits,
    ssh_hook=sshHook,
    dag=dag)

    download_radar >> download_orbits
