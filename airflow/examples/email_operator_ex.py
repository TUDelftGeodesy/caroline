#################################################################################
# Email Operator Example                                                     #
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
from airflow.utils.dates import days_ago
# import custom operator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.email import EmailOperator
# hook to Spider
# sshHook = SSHHook(ssh_conn_id='spider_mgarcia')

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
    dag_id='email-operator',
    default_args=default_args,
    description='Test DAG email',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'example', 'test'],
) as dag:

    def start_task():
        print("task started")
        
    start_task = PythonOperator(
        task_id='executetask',
        python_callable=start_task,
        dag=dag)

    # task with DownloadOperator
    send_email = EmailOperator(
    task_id='send_email',
    to='m.g.garciaalvarez@tudelft.nl',
    subject='airflow test',
    html_content = 'This is the content',
    dag=dag)
    
    # dependencies
    send_email.set_upstream(start_task)
