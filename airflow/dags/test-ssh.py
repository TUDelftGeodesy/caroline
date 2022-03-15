from datetime import timedelta, datetime
import airflow
from airflow import DAG
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.contrib.hooks.ssh_hook import SSHHook
sshHook = SSHHook(ssh_conn_id='test-ssh-connection')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'start_date': datetime.now() - timedelta(minutes=20),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
dag = DAG(dag_id='testing_stuff',
          default_args=default_args,
          schedule_interval='0,10,20,30,40,50 * * * *',
          dagrun_timeout=timedelta(seconds=120))

t1_bash = """
echo 'Hello World'
"""
t1 = SSHOperator(
    ssh_conn_id='ssh_default',
    task_id='test_ssh_operator',
    command=t1_bash,
    ssh_hook=sshHook,
    dag=dag)