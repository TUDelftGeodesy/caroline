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
import uuid
from datetime import timedelta

from click import command
from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.operators.email import EmailOperator
from airflow.contrib.operators.ssh_operator import SSHOperator 
from airflow.utils.dates import days_ago
# import custom operators
from download_operator import DownloadOperator
from sbatch_operator import SBATCHOperator
# hook to Spider
sshHook = SSHHook(ssh_conn_id='spider_mgarcia') 


uuid.UUID
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['name@tudelft.nl'],
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
    dag_id='interferogram2',
    default_args=default_args,
    description='Test DAG download',
    schedule_interval=timedelta(days=6),
    start_date=days_ago(0),
    tags=['caroline', 'template'],
) as dag:

    # Commands
    cmd_download_radar ="""
    python main.py conf {{dag_run.conf["start_date"]}} {{dag_run.conf["end_date"]}} -f {{dag_run.conf["geometry"]}} -o {{dag_run.conf["orbit_direction"]}} 
    """

    cmd_download_precise_orbits ="""
    python orbits.py conf {{dag_run.conf["start_date"]}} {{dag_run.conf["end_date"]}} --type POE
    """

    sbatch_body = """
    # load dependencies
    source /project/caroline/Software/bin/init.sh &&
    module load python/3.9.6  gdal/3.4.1 proj/8.2.1
    # Activate virtual environment 
    source /project/caroline/Software/caroline/caroline-venv/bin/activate
    cd /project/caroline/Share/users/caroline-mgarcia
    # path to processing eninge
    PROGRAM="/project/caroline/Software/caroline/processing/processing/interferogram/main.py"
    python $PROGRAM --start_date {{dag_run.conf['start_date']}} --end_date {{dag_run.conf['end_date']}} --mdate {{dag_run.conf["master_date"]}} --processes {{dag_run.conf["processes"]}} --name {{dag_run.conf["stack_name"]}} --file {{dag_run.conf["geometry"]}} --resplanar {{dag_run.conf["planar_resolution"]}} --pol {{dag_run.conf["polarisation"]}}  || exit 91
    """

    # TODO: templated code is not rendering. Check templated fields in SSHOperator and string concatenation.
    copy_prduct = """
    # Path to products directory for sentinel1. Depends on RIPPL configuration
    PRODUCT_PATH="/project/caroline/Share/users/caroline-mgarcia/products/sentinel1/"{{dag_run.conf['stack_name']}}
    ZIP_FILE = "interferogram-"+={{dag-run.conf['stack_name']}}+=".zip"
    zip -r ${PRODUCT_PATH}/${ZIP_FILE} ${PRODUCT_PATH}/interferogram
    scp ${PRODUCT_PATH}/${ZIP_FILE}  caroline-mgarcia@spider.surfsara.nl:/temp
    """

    # Tasks:
    download_radar = DownloadOperator(
    task_id='download_radar_datasets',
    command=cmd_download_radar,
    ssh_hook=sshHook,
    dag=dag)

    download_precise_orbits = DownloadOperator(
    task_id='download_precise_orbits',
    command=cmd_download_precise_orbits,
    ssh_hook=sshHook,
    dag=dag)

    create_interferogram = SBATCHOperator(
    task_id='create_interferogram',
    sbatch_commands=sbatch_body,
    script_name="test_sbatch.sh",
    max_time='59:59',
    frequency = '10s',
    output_dir= "/project/caroline/Share/users/caroline-mgarcia/sbatch",
    cores=2,
    ssh_hook=sshHook,
    dag=dag)

    zip_product = SSHOperator(
    task_id='zip_product',
    command= copy_prduct,
    ssh_hook=sshHook,
    dag=dag
    )


    # TODO: implement tasks  copying product to Airflow VM
    # TODO: implement tasks for sending email with product as attachment


    send_email = EmailOperator(
    task_id='send_png',
    to=['m.g.garciaalvarez@tudelft.nl'],
    subject='New Product: Interfereogram',
    html_content = 'A new interferogram is ready. Find a visualization in the attachment',
    dag=dag)



    # dependencies
    # download_radar >> download_precise_orbits >> create_interferogram >> 
    zip_product >> send_email

