#################################################################################
# DAG for creating Inteferograms using Doris-RIPPL                              
#################################################################################
# This DAG searches and download Sentinel-1 datasets and orbit files based on
# time and geographic area. Downloaded datsets are used to produce several 
# products including an interferogram using Doris RIPPL

# TEMPLATED PARAMETERS:
# start_date
# end_date
# master_date
# orbit_direction
# geometry
# orbit_type
# planar_resolution
# polarisation
# processes
# stack_name

# Running the DAG:
# =================
# Values for templated parameters must be passed as Json.
# E.g.
# {"start_date":"20220410", 
# "end_date":"20220410", 
# "geometry":"POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))"}

#################################################################################
from datetime import timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.operators.email import EmailOperator
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.utils.dates import days_ago
# import custom operators
from download_operator import DownloadOperator
from sbatch_operator import SBATCHOperator
# hook to Spider
sshHook = SSHHook(ssh_conn_id='spider_mgarcia')


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['net_id@tudelft.nl'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='interferogram',
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

    cmd_file_compression="""
    zip -r /project/caroline/Share/users/caroline-mgarcia/products/sentinel1/{{dag_run.conf["stack_name"]}}/interferogram.zip /project/caroline/Share/users/caroline-mgarcia/products/sentinel1/{{dag_run.conf["stack_name"]}}/interferogram 
    """

    # WARNING: -o StrictHostKeyChecking=no will automatically accepts connections from any host. 
    # This reduces security. Ideally host verification is handled in a different way.
    cmd_transfer_file ="""
    scp -i /opt/airflow/ssh/caroline_rsa -o StrictHostKeyChecking=no caroline-mgarcia@spider.surfsara.nl:/project/caroline/Share/users/caroline-mgarcia/products/sentinel1/{{dag_run.conf["stack_name"]}}/interferogram.zip /opt/airflow/data/temp/interf-{{dag_run.conf["stack_name"]}}.zip
    """

    cmd_clean_up="""
    rm /project/caroline/Share/users/caroline-mgarcia/products/sentinel1/{{dag_run.conf["stack_name"]}}/interferogram.zip
    """

    email_message= """
    <p>Hello,</p> 
    <p>A new interferogram has been produced for <b>{{dag_run.conf["stack_name"]}}</b>. See attachment.</p> 
    <p>Greetings,</p>
    <p><em>Caroline Development Team</em></p>
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

    # Prepares and compresses interferogram file for tranfer
    compress_file = SSHOperator(
    task_id='compress_product',
    command=cmd_file_compression,
    ssh_hook=sshHook,
    dag=dag
    )

    # Copies interferogram files to Airflow Host
    transfer_file = BashOperator(
    task_id='transfer_product',
    bash_command=cmd_transfer_file,
    dag=dag
    )

    # Deletes compressed file at Spider
    clean_up = SSHOperator(
    task_id='clean_up',
    command=cmd_clean_up,
    ssh_hook=sshHook,
    dag=dag
    )

    send_email = EmailOperator(
    task_id='email_notification',
    to=['m.g.garciaalvarez@tudelft.nl'],
    #'n.h.jansen@tudelft.nl', 'F.J.vanLeijen@tudelft.nl'],
    subject='New Sentinel-1 Product',
    html_content = email_message,
    files=['/opt/airflow/data/temp/interf-{{dag_run.conf["stack_name"]}}.zip'],
    dag=dag
    )

    # dependencies
    [ download_radar, download_precise_orbits ] >> create_interferogram >> compress_file >> transfer_file >> [send_email, clean_up]
