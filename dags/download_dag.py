"""
A DAG example for the download of data from ASF, using the Python Operator
Must provide your own account credentials
"""

from datetime import timedelta

# Imports for custom modules
# Custome modules must be copied the 'code' volume
import sys
sys.path.insert(0, '/opt/airflow/code/download')
import connector
import asf
import data_product

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago


# define objects/functions used accross tasks
con = connector.Connector("USERNAME", "PASSWORD", 'https://api.daac.asf.alaska.edu/', retain_auth=True)
con.test_connection()
api = asf.ASF(con)

def products_to_dict(product_list):
    """
    Converts dataclasses into nested dictionary. XCom requires JSON for metadata 
    """
    
    dictonary={}
    count=1
    for product in product_list:
        dictonary[str(count)] = product.__dict__
        count+=1
    return dictonary

def dict_to_product_list(dictionary, data_class=data_product.Product):
    """
    Converts nested dictionary (products) into list of dataclasses (products). Required by search.download()
    """
    #TODO: needs general and clean code for this function
    values = dictionary.values()
    products_list = []

    for v in values:
        keys = list(v.keys())
        product = data_class(v[keys[0]], v[keys[1]], v[keys[2]], v[keys[3]], v[keys[4]], v[keys[5]], v[keys[6]], v[keys[7]], v[keys[8]], v[keys[9]] )
        products_list.append(product)

    return products_list

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

        search_results=api.search('POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))',
        '2018-04-22', '2018-05-08', orbit_direction='Ascending',
        sensor_mode='IW', product='SLC', instrument_name='Sentinel-1')

        results = products_to_dict(search_results)
        ti.xcom_push(key='search_results', value=results)

    def dowload_data(ti):

        search_results = ti.xcom_pull(key='search_results', task_ids='search')
        results_list = dict_to_product_list(search_results)
        api.download([ results_list[0] ], '/opt/airflow/data/') # limit download to 1 item
        
        print('download completed')

    # XCom pass metadata between tasks. Pushes are default, but pulls are not
    # Tasks
    search_task = PythonOperator(
        task_id = 'search',
        python_callable=search_api,

    )

    download_task = PythonOperator(
        task_id = 'download',
        python_callable=dowload_data,
    )

    # Dependencies
    search_task >> download_task
        
