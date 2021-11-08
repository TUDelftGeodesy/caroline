"""
A DAG for the download of data from ASF.
Must provide your own account credentials
"""

from datetime import timedelta

import sys
sys.path.insert(0, './code/download')
from download import connector
from download.asf import ASF

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# define objects reusable accross tasks
con = connector.Connector("USERNAME", "PASSWORD", 'https://api.daac.asf.alaska.edu/', retain_auth=True)
con.test_connection()
api = ASF(con)

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
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
    'caroline-download',
    default_args=default_args,
    description='Test DAG download',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline'],
) as dag:
    
    def search_api(ti):

        api=ti.xcom_pull(key='api_connector', task_ids='get_connect_api_data_{0}.fc')
        search_results=api.search('POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))',
        '2018-04-22', '2018-05-08', orbit_direction='Ascending',
        sensor_mode='IW', product='SLC', instrument_name='Sentinel-1')

        ti.xcom_push(key='search_results', value=search_results)

    # xcom post values to database, therefore objects might be terminated

    def dowload_data(ti):
        search_results = ti.xcom_pull(key='search_results', task_ids='get_search_results_data_{0}.fc')
        search_api.download(search_results, './data/') 
        
        print('download completed')

    # Tasks

    # XCom to pass metadata between tasks, default at push, but not with pull

    search_task = PythonOperator(
        task_id = 'search',
        python_callable=search_api(),

    )

    download_task = PythonOperator(
        task_id = 'download',
        python_callable=dowload_data,
    )

    search_task >> download_task
        




