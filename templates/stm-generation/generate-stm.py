"""Example script for calculating SLCs from interferograms.

This .py script is designed to be executed with a Dask SLURMCluster on a SLURM managed HPC system.
It should be executed through a SLURM script by `sbatch` command.
Please do not run this script by "python xxx.py" on a login node.
"""

import logging
import socket

from dask.distributed import Client
from dask_jobqueue import SLURMCluster
from depsi.classification import ps_selection
from depsi.io import read_slc_stack
from depsi.point_quality import detect_outliers_stm, stm_add_incremental_recal_nad_nmad, stm_partitioning
from depsi.utils import add_stm_time_deltas, project_stm_coordinates, stm_compute_single_time_differences

from caroline.config import get_config

CONFIG = get_config()
JOB_DEFINITIONS = get_config(f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False)

# Make a logger to log the stages of processing
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()  # create console handler
ch.setLevel(logging.INFO)
logger.addHandler(ch)

# ############## INPUT VARIABLES

slc_path = "**crop_to_zarr_directory**/**crop_to_zarr_output_name**.zarr"

# STM save path
stm_save_path = "**stm_output_directory**/**stm_output_name**.zarr"

# PS Selection based on initialization
ps_selection_mode = "**stm_generation:stm_generation-settings:ps-selection:mode**"
if ps_selection_mode == "initialization":
    start_date_ps_selection = (
        "**stm_generation:stm_generation-settings:ps-selection:initialization-mode-settings:start-date**".replace(
            "-", ""
        )
    )
    initialization_length = int(
        "**stm_generation:stm_generation-settings:ps-selection:initialization-mode-settings:initialization-length**"
    )
else:
    start_date_ps_selection = None
    initialization_length = None

# Recalibrated NAD and NMAD settings
increment_mode = "**stm_generation:stm_generation-settings:incremental-statistics:increment-mode**"
recalibration_jump_size = eval(
    "**stm_generation:stm_generation-settings:incremental-statistics:recalibration-jump-size**"
)

# PS selection method
ps_selection_method = "**stm_generation:stm_generation-settings:ps-selection:method**"
threshold = eval("**stm_generation:stm_generation-settings:ps-selection:threshold**")
chunks_ps_selection = 1000

# Input variables for the outlier detection
do_ps_outlier_detection = (
    True if "**stm_generation:stm_generation-settings:outlier-detection:do-outlier-detection**" == 1 else False
)
ps_window_size_outliers = int("**stm_generation:stm_generation-settings:outlier-detection:window-size**")
ps_outlier_detection_db = True if "**stm_generation:stm_generation-settings:outlier-detection:db-mode**" == 1 else False
ps_n_sigma_outliers = int("**stm_generation:stm_generation-settings:outlier-detection:n-sigma**")

# Input variables for the partitioning
do_ps_partitioning = True if "**stm_generation:stm_generation-settings:partitioning:do-partitioning**" == 1 else False
ps_partitioning_search_method = "**stm_generation:stm_generation-settings:partitioning:search-method**"
ps_partitioning_cost_function = "**stm_generation:stm_generation-settings:partitioning:cost-function**"
ps_db_partitioning = True if "**stm_generation:stm_generation-settings:partitioning:db-mode**" == 1 else False
ps_min_obs_partition = int("**stm_generation:stm_generation-settings:partitioning:min-partition-length**")
partitioning_output_layers = tuple(
    eval("**stm_generation:stm_generation-settings:partitioning:undifferenced-output-layers**")
)
partitioning_sd_output_layers = tuple(
    eval("**stm_generation:stm_generation-settings:partitioning:single-difference-output-layers**")
)

# Compute temporal differences
ps_mother_epoch_sd = "**stm_generation:stm_generation-settings:single-differences:mother**".replace("-", "")

projection = "**stm_generation:stm_generation-settings:extra-projection**"
do_projection = False
if projection not in ["", "None"]:
    do_projection = True


# ## FUNCTIONALITY
# Start cluster


def get_free_port():
    """Get a non-occupied port number."""
    sock = socket.socket()
    sock.bind(("", 0))  # Bind a port, it will be busy now
    freesock = sock.getsockname()[1]  # get the port number
    sock.close()  # Free the port, so it can be used later
    return freesock


N_WORKERS = JOB_DEFINITIONS["jobs"]["stm_generation"]["bash-file"]["bash-file-slurm-cluster"][
    "slurm-cluster-n-workers"
]  # Manual input: number of workers to spin-up
FREE_SOCKET = get_free_port()  # Get a free port
cluster = SLURMCluster(
    name="dask-worker",  # Name of the Slurm job
    queue="normal",  # Name of the node partition on your SLURM system
    cores=4,  # Number of cores per worker
    memory="30 GB",  # Total amount of memory per worker
    processes=1,  # Number of Python processes per worker
    walltime=JOB_DEFINITIONS["jobs"]["stm_generation"]["bash-file"]["bash-file-slurm-cluster"][
        "slurm-cluster-worker-time"
    ],  # Reserve each worker for X hour
    scheduler_options={"dashboard_address": f":{FREE_SOCKET}"},  # Host Dashboard in a free socket
)

cluster.scheduler.no_workers_timeout = 3 * 60 * 60  # If no workers are detected for 3 hours, terminate (#208)
cluster.scale(jobs=N_WORKERS)
client = Client(cluster)

# ############ LOAD THE SLCS FROM ZARR ###############
logger.info("Start reading.")

slcs = read_slc_stack(slc_path)

logger.info("Finished reading.")

# ######## POINT SELECTION WITH THE PARAMETERS ABOVE ############
logger.info("Start selection.")

stm = ps_selection(
    slcs,
    method=ps_selection_method,
    threshold=threshold,
    ps_selection_start_date=start_date_ps_selection,
    ps_selection_end_date=initialization_length,
    output_chunks=chunks_ps_selection,
    mem_persist=False,
)

logger.info(f"Selected {stm.sizes['space']} PS points")

# Add the incremental or recalibration NAD / NMAD to the STM
stm = stm_add_incremental_recal_nad_nmad(
    stm, mode=increment_mode, method=ps_selection_method, recalibration_jump_size=recalibration_jump_size
)

logger.info(f"Finished {increment_mode} {ps_selection_method}.")

# Add RD coordinates to the STM
if do_projection:
    stm = project_stm_coordinates(stm, projection)

    logger.info(f"Added projection {projection}.")

# Add time deltas to the STM
stm = add_stm_time_deltas(stm)

logger.info("Finished time deltas.")

# Add single differences to the STM
stm = stm_compute_single_time_differences(stm, ps_mother_epoch_sd)

logger.info("Finished single differences.")

if do_ps_partitioning:
    logger.info("Starting partitioning.")
    stm = stm_partitioning(
        stm,
        db_partitioning=ps_db_partitioning,
        search_method=ps_partitioning_search_method,
        cost_model=ps_partitioning_cost_function,
        min_partition_size=ps_min_obs_partition,
        amplitude_variable_name="amplitude",
        output_variable_prefix="partition",
        output_variables=partitioning_output_layers,
    )
    logger.info("Finished normal partitions.")

    stm = stm_partitioning(
        stm,
        db_partitioning=ps_db_partitioning,
        search_method=ps_partitioning_search_method,
        cost_model=ps_partitioning_cost_function,
        min_partition_size=ps_min_obs_partition,
        amplitude_variable_name="sd_amplitude_unnormalized",
        output_variable_prefix="partition_sd",
        output_variables=partitioning_sd_output_layers,
    )
    logger.info("Finished single difference partitions.")

# Rechunk to prevent inconsistent chunks
stm = stm.chunk({"time": -1, "space": chunks_ps_selection})

# Do outlier detection
if do_ps_outlier_detection:
    logger.info("Starting outlier detection.")
    stm = detect_outliers_stm(
        stm,
        db_outlier_detection=ps_outlier_detection_db,
        window_size=ps_window_size_outliers,
        n_sigma=ps_n_sigma_outliers,
    )
    logger.info("Finished outlier detection.")

# Save
stm.to_zarr(stm_save_path, mode="w")
logger.info("Finishing... Closing client.")

client.close()
