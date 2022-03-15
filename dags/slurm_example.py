# A DAG for testing the Slurm Operator on Spider 
from datetime import timedelta, datetime
from time import sleep

from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
# custom operator
from slurm_operator import SlurmOperator
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
    dag_id='slurm_example',
    default_args=default_args,
    description='Test DAG download',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'test'],
) as dag:

    batch_command = """
    sbatch /project/caroline/Software/slurm/welcome-to-spider.sh
    """
    dir_output_file = "/project/caroline/Software/slurm/"

    run_slurm_job = SlurmOperator(
    task_id='slurm_job',
    sbatch_command=batch_command,
    sleep_time = '20s',
    output_file= dir_output_file,
    ssh_hook=sshHook,
    dag=dag)

    run_slurm_job
