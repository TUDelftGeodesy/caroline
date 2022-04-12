##############################################################
# Sbatch Operator Example                                     #
##############################################################
# This example shows how to use the custom SBATCHOperator in 
# a DAG. 
# We assume that the operator is available via the plugings
# directory at the airflow root directory.
# A sshHook to an instance of Slurm is required.
#
# The SBATCHOperator inherits from the SSHOperator and
# was extended with the following arguments:
    # sbatch_command (str): commands for the body of the sbatch script.
    # script_name (str): name for the sbash script. A '.sh' file
    # max_time (str): maximum run time for the slurm job, [HH:MM:SS] or [MM:SS] or [minutes]
    # frequency (str): time interval at which the status of a job will be checked. Default is 1 minute.
    # output_dir (str): path to directory for the  sbatch script and the slurm output file. If None, output file will be in
    #     home directory.
    # cores: number of cores to request to the cluster.
    # tasks: number of tasks to request to the cluster.
    # nodes: number of node to request to the cluster.
    # partition: partition type.
    # qos: quality of service to request to the cluster.
##############################################################

from asyncio import tasks
from datetime import timedelta, datetime
from time import sleep

from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.utils.dates import days_ago
# custom operator
from sbatch_operator import SBATCHOperator
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
    dag_id='sbatch-operator',
    default_args=default_args,
    description='Test DAG with sbatch operator',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(0),
    tags=['caroline', 'example'],
) as dag:

    # Define command to start sbatch job
    sbatch_body = """
    echo ""
    echo "====================================================="
    echo "     Dear" $USER "Welcome to Spider         "
    echo "====================================================="

    echo ""
    PROJECT=$(echo $USER | cut -d '-' -f1)
    echo "The project space for your project ${PROJECT} is located at"
    ls -d /project/$PROJECT
    echo "which consists of the following directories"
    ls /project/$PROJECT

    echo ""
    echo "Create some random numbers in fil:qe 'randomlist':"
    for i in {1..10}
    do
        echo $RANDOM >> randomlist
    done
    cat $PWD/randomlist

    echo ""
    echo "You just executed your first job on "$HOSTNAME" with a job ID "$SLURM_JOBID
    sleep 30s
    """

    name = "sbatch_test.sh"
    # Define directory for job-ID.out file
    dir_output_file = "/project/caroline/Share/users/caroline-mgarcia/sbatch/"

    # Define Task with SlurmOperator
    run_slurm_job = SBATCHOperator(
        task_id = 'sbatch_job',
        sbatch_commands = sbatch_body,
        script_name = name,
        max_time = '15:00',
        frequency = '15s',
        output_dir = dir_output_file,
        ssh_hook = sshHook,
        dag=dag
    )

    # Dependencies
    run_slurm_job