import glob
import logging
import socket

import sarxarray as sxr
from dask.distributed import Client
from dask_jobqueue import SLURMCluster
from depsi.utils import crop_slc_spacetime

from caroline.config import get_config

CONFIG = get_config()
JOB_DEFINITIONS = get_config(f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False)

logger = logging.getLogger(__name__)

znap_output_path = "**snap-output-path**"
zarr_output_path = "**znap_to_zarr_output_filename**.zarr"
aoi_path = "**general:shape-file:directory**/**general:shape-file:aoi-name**_shape.shp"


def get_free_port():
    """Get a non-occupied port number."""
    sock = socket.socket()
    sock.bind(("", 0))  # Bind a port, it will be busy now
    freesock = sock.getsockname()[1]  # get the port number
    sock.close()  # Free the port, so it can be used later
    return freesock


# ---- Config 2: Dask configuration ----

# Option 1: Initiate a new SLURMCluster
# Uncomment the following part to setup a new Dask SLURMCluster
N_WORKERS = JOB_DEFINITIONS["jobs"]["znap_to_zarr"]["bash-file"]["bash-file-slurm-cluster"][
    "slurm-cluster-n-workers"
]  # Manual input: number of workers to spin-up
FREE_SOCKET = get_free_port()  # Get a free port
cluster = SLURMCluster(
    name="dask-worker",  # Name of the Slurm job
    queue="normal",  # Name of the node partition on your SLURM system
    cores=4,  # Number of cores per worker
    memory="30 GB",  # Total amount of memory per worker
    processes=1,  # Number of Python processes per worker
    walltime=JOB_DEFINITIONS["jobs"]["znap_to_zarr"]["bash-file"]["bash-file-slurm-cluster"][
        "slurm-cluster-worker-time"
    ],  # Reserve each worker for X hour
    scheduler_options={
        "dashboard_address": f":{FREE_SOCKET}",  # Host Dashboard in a free socket
    },
)
cluster.scheduler.no_workers_timeout = 3 * 60 * 60  # If no workers are detected for 3 hours, terminate (#208)

cluster.scale(jobs=N_WORKERS)
client = Client(cluster)


znaps = glob.glob(f"{znap_output_path}/*-coreg.znap")

logger.info("Reading data...")
data = sxr.from_znap(znaps)
data = data.rename({"latitude": "lat", "longitude": "lon", "elevation": "h"})

logger.info("Cropping...")
cropped_data = crop_slc_spacetime(data, aoi_filename=aoi_path)

cropped_data = cropped_data.chunk({"azimuth": 4000, "range": 4000, "time": 1})

# removing the metadata to be able to write to zarr again
cropped_data.attrs = {}

logger.info("Writing...")
cropped_data.to_zarr(zarr_output_path, mode="w")

logger.info("Finished! Closing client...")
client.close()
