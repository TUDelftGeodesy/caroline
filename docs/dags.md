# DAGs

DAGs define pipelines in Apache Airflow. 

## Deploying DAG in airflow

To deploy and run a DAG in Apache Airflow:

1. Create a DAG (a python script). See the [Airflow Documentaton](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html#example-pipeline-definition)
2. Copy the python script to `/opt/airflow/dags` Airflow automatically deploys dag in this directory. It may take one or two minutes to appear on the web UI.
3. Go to the web UI, then DAGs menu, click on the DAG you want to run; press the play button on the top-right corner, and click on trigger DAG 

## DAG templates

[Templating](https://www.astronomer.io/guides/templating/) is a way to pass dynamic information to DAGs. Here, we use templates as a way to reuse pipelines. 

Below are a few examples of how templating can be used along with the [Custom Operators](custom-operators.md)

### Downloading Radar Datasets

1. Definition:

```python
########################################################
# Templated DAG for Downloadiong Sentinel-1 Datesets   #
########################################################

from datetime import timedelta
from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
# import custom operators
from download_operator import DownloadOperator
# hook to Spider
sshHook = SSHHook(ssh_conn_id='spider_mgarcia') 

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['username@domain.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
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

    # Tasks:
    download_radar = DownloadOperator(
    task_id='download_radar_datasets',
    command=cmd_download_radar,
    ssh_hook=sshHook,
    dag=dag)
    
    # dependencies
    download_radar 
```

2. Running:
   - Go to the web UI, then DAGs menu, click on the DAG you want to run; press the play button on the top-rigth corner, and click on **trigger DAG/w config**
   - On the **Configuration JSON** provide a JSON file with the values for the templated arguments. For example:

        ```json
        {"start_date":"20160101", "end_date":"20160120", "orbit_direction":"Descending", "geometry":"amsterdam.kml" }
        ```

### Downloading Orbits

1. Definition:

```python
##############################################
# Templated DAG for Downloadiong Orbits      #
##############################################

from concurrent.futures import process
from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
# import custom operators
from download_operator import DownloadOperator
from sbatch_operator import SBATCHOperator
# hook to Spider
sshHook = SSHHook(ssh_conn_id='spider_mgarcia') 

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['usernam@domain.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='dowload-orbits',
    default_args=default_args,
    description='Test dowload of obits',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'test', 'template'],
) as dag:

    cmd_download_orbits ="""
    python orbits.py conf {{dag_run.conf["start_date"]}} {{dag_run.conf["end_date"]}} --type {{dag_run.conf["orbit_type"]}}
    """
    # Tasks
    download_orbits = DownloadOperator(
    task_id='download_orbits',
    command=cmd_download_orbits,
    ssh_hook=sshHook,
    dag=dag)

    # dependencies
    download_orbits 
```

2. Running:
   - Go to the web UI, then DAGs menu, click on the DAG you want to run; press the play button on the top-right corner, and click on **trigger DAG/w config**
   - On the **Configuration JSON** provide a JSON file with the values for the templated arguments. For example:

        ```json
        {"start_date":"20160101", "end_date":"20160120", "orbit_type": "RES"}
        ```

### Processing Data: Interferogram

1. Definition:
   
```python
################################################
# Templated DAG for creating Inteferograms     #
################################################

from concurrent.futures import process
from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
# import custom operators
from sbatch_operator import SBATCHOperator
# hook to Spider
sshHook = SSHHook(ssh_conn_id='spider_mgarcia') 

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['user@domain.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
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
    # path to processing engine
    PROGRAM="/project/caroline/Software/caroline/processing/processing/interferogram/main.py"
    python $PROGRAM --start_date {{dag_run.conf['start_date']}} --end_date {{dag_run.conf['end_date']}} --mdate {{dag_run.conf["master_date"]}} --process {{dag_run.conf["processes"]}} --name {{dag_run.conf["stack_name"]}} --file {{dag_run.conf["geometry"]}} --resplanar {{dag_run.conf["planar_resolution"]}} --pol {{dag_run.conf["polarisation"]}}  || exit 91
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

```


2. Running:
   - Go to the web UI, then DAGs menu, click on the DAG you want to run; press the play button on the top-right corner, and click on **trigger DAG/w config**
   - On the **Configuration JSON** provide a JSON file with the values for the templated arguments. For example:

        ```json
        {"start_date":"20160101", "end_date":"20160120", "master_date":"20160107", "orbit_direction":"Descending", "geometry":"/project/caroline/Share/users/caroline-mgarcia/amsterdam.kml", "orbit_type": "RES", "planar_resolution": 500, "polarisation": "VV", "processes": 4, "stack_name": "test_stack" }
        ```
    > IMPORTANT: This DAG expects that datasets were already downloaded, and that the [configuration for the processing engine](processing-engine.md) has been set correctly.
   
   