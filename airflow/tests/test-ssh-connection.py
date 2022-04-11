#######################################################################
# DAG to test connection to Spider via SSH                            #
#######################################################################
# Prerequisits:
# - An ID of an existing SSH connnection to Spider 
#   with the following configuration for extras:
# 
#   {"key_file": "</container/path/to/ssh_key>", 
#   "conn_timeout": "10", "compress": "false", 
#   "look_for_keys": "false", 
#   "allow_host_key_change": "true"}
#
# Expected Output:
# Prints "Hello World" to standard output on remote
# terminal
#######################################################################

from datetime import timedelta, datetime
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.contrib.hooks.ssh_hook import SSHHook
sshHook = SSHHook(ssh_conn_id='spider_mgarcia') # Id of SSH connection

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
    dag_id='test-ssh-connection',
    default_args=default_args,
    description='Test DAG download',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'test'],
) as dag:

    bash_command = """
    echo 'Hello World'
    """

    task_1 = SSHOperator(
        task_id='hello_world',
        command=bash_command,
        ssh_hook=sshHook,
        dag=dag)

    # Dependencies
    task_1
