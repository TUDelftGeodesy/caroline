# Airflow

Airflow provides a way to automate the processing workflow required for the productio of data pruducts in Caroline.

We are running version *2.2.4*  of Apache Airflow using Docker. 

## Installing Apache Airflow

When running apache airflow for the very firts time, do the following:

1. Copy the the [docker-compose.yalm](assets/scripts/docker-compose.yalm) file to the directory that will serve as root directory.
2. Create the following directories: `dags, logs, plugins, ssh`
3. Change the permisions of directories with `chmod -R 777 dags/ logs/ plugins/ ssh/`
4. Create an `.env` file with the user id: `echo -e "AIRFLOW_UID=$(id -u)" > .env`
5. Define and set the values for the following variable in `.env`:
   
   ```shell
    AIRFLOW_UID=552041
    AIRFLOW__WEBSERVER__BASE_URL=http://caroline.citg.tudelft.nl:8080
    AIRFLOW__SMTP__SMTP_HOST=<require only for the Email Operator>
    AIRFLOW__SMTP__SMTP_USER=<require only for the Email Operator>
    AIRFLOW__SMTP__SMTP_PASSWORD=<require only for the Email Operator>
    AIRFLOW__SMTP__SMTP_PORT=<require only for the Email Operator>
    AIRFLOW__SMTP__SMTP_MAIL_FROM=<require only for the Email Operator>
    _AIRFLOW_WWW_USERNAME=<initial admin username>
    _AIRFLOW_WWW_PASSWORD=<initial admin password>
    ```

6. Initialize the services with `docker-compose up airflow-init`
7. Start up the containers in detached mode: `docker-compose up -d`

### Reinstalling Apache Airflow

> Warning: this will permanently delete all configurations, DAGs and execution histories.

1. Stop the contatiners.
2. Run `docker-compose down --volumes --remove-orphans`
3. Delete all directories with `rm -rf '<DIRECTORY>'`
4. Follow the instruction in the previous section to install Apache Airflow.


## Custom Operators

We implemented three custom operators for executing tasks on Spider. 

|Operator | Inherits From|      Purpose |
|---------|--------------|--------------|
|SlurmOperator|SSHOperator| Submits a slurm job to Spider|
|DownloadOperator|SSHOperator| Executes download tasks on the Download Engine on Spider|
|SBATCHOperator | SSHOperator | Prepares and submits slurm jobs using the `sbatch` command to Spider|

### Slurm Operator

It prepares and submits slrum jobs to Spider using the slurm commands, e.g. `sbatch`. The job status is monitored until completed or fail. It inherits properties and methods from the SSHOperator. It requires an SSHHook.

|Argument| Description|
|--------|-------------|
|**command** |slum command or run or sumbit a job E.g., `sbatch <path to script.sh>`|
|**monitor_time** | frequency at which the status of a job will be checked. Default is 1 minute.|
|**output_file** | path to the directory for the slurm output file. If `None`, output file will be in home directory.|
|**ssh_hook** | SSHHook |

### Download Operator

It executes commands on the Download Engine. It activates virtual environment and modules for the Download Engine. It inherits properties and methods from the SSHOperator, and requires an SSHHook.

|Argument| Description|
|--------|-------------|
| **command** | command to be executed by the download engine |
|**ssh_hook** | SSHHook |

### SBATCH Operator

It prepares and submits slrum jobs on Spider using the sbatch command. The job status is monitored until complete or fails. It inherits properties and methods from the SSHOperator and requires an SSHHook.

|Argument| Description|
|--------|-------------|
| **sbatch_command** | commands for the body of the sbatch script|
| **script_name** | name for the sbash script. A '.sh' file|
| **max_time** | maximum run time for the slurm job, [HH:MM:SS] or [MM:SS] or [minutes] |
| **frequency** | time interval at which the status of a job will be checked. Default is 1 minute|
| **output_dir** | path to the directory for the  sbatch script and the slurm output file. If None, the output file will be in home directory|
| **cores** | number of cores to request to the cluster |
|    **tasks** | number of tasks to request to the cluster|
|   **nodes** | number of nodes to request to the cluster|
|   **partition** | partition type|
|   **qos** | quality of service to request to the cluster|
|**ssh_hook** | SSHHook |


## DAGs

We provide a few DAGs (Directed Acyclic Graphs) as examples for the case for Caroline.

### Using the Slurm Operator

```python
#####################################
# Slurm Operator Example            #
#####################################

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
# You can override them on a per-task basis during 
# operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['m.g.garciaalvarez@tudelft.nl'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='slurm-operator',
    default_args=default_args,
    description='Test DAG download',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'example'],
) as dag:

    # Define command for the operator
    batch_command = """
    sbatch /project/caroline/Software/slurm/welcome-to-spider.sh
    """
    # Define directory for job-ID.out file
    dir_output_file = "/project/caroline/Software/slurm/"

    # Define Task with SlurmOperator
    run_slurm_job = SlurmOperator(
    task_id='slurm_job',
    sbatch_command=batch_command,
    monitor_time = '20s',
    output_file= dir_output_file,
    ssh_hook=sshHook,
    dag=dag)

    # Dependencies
    run_slurm_job
```

### Using the Download Operator

```python
########################################
# Download Operator Example            #
########################################

from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
# import custom operator
from download_operator import DownloadOperator
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
}

with DAG(
    dag_id='dowload-operator',
    default_args=default_args,
    description='Test DAG download',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'example'],
) as dag:

    # command for Download Engine
    cmd_download_radar ="""
    PROGRAM=<path to download engine program>
    python $PROGRAM conf 20211219 20211230 --aoi "POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))" --orbit DES
    """

    # task with DownloadOperator
    download_radar = DownloadOperator(
    task_id='download_radar',
    command=cmd_download_radar,
    ssh_hook=sshHook,
    dag=dag)
    
    # dependencies
    download_radar 
```

### Using the SBATCH Operator

```python
############################################
# Sbatch Operator Example                  #
############################################

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
}

with DAG(
    dag_id='processing-inter',
    default_args=default_args,
    description='Test DAG processing',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'test', 'template'],
) as dag:

    # Commands for the body of the Sbatch script
    sbatch_body = """
    # load dependencies
    source /project/caroline/Software/bin/init.sh &&
    module load python/3.9.6  gdal/3.4.1 proj/8.2.1
    # Activate virtual environment 
    source /project/caroline/Software/caroline/caroline-venv/bin/activate
    cd /project/caroline/Share/users/caroline-mgarcia
    # path to processing engine
    PROGRAM="<path to the CLI interface of the download engine>"
    python $PROGRAM --start_date 20160101 --end_date 20160120 --mdate 20160107 --process 4 --name test_stack --file /project/caroline/Share/users/caroline-mgarcia/amsterdam.kml --resplanar 500 --pol VV  || exit 91
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

> IMPORTANT: When using this operator, the  `|| exit <error code>` must be added at the end of any critical or major command. This is because the final status of the slurm job is determined by the success or failure of the last statement in the sbatch script. In other words, `|| exit 91` will enforce that the job is reported a failed if the `python $PROGRAM` fails.

