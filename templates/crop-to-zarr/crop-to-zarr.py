"""Example script for calculating SLCs from interferograms.

This .py script is designed to be executed with a Dask SLURMCluster on a SLURM managed HPC system.
It should be executed through a SLURM script by `sbatch` command.
Please do not run this script by "python xxx.py" on a login node.
"""

import logging
import os
import socket
from datetime import datetime
from pathlib import Path

import dask.array as da
import numpy as np
import sarxarray
import xarray as xr
from dask.distributed import Client
from dask_jobqueue import SLURMCluster
from depsi.io import read_metadata
from depsi.slc import ifg_to_slc
from depsi.utils import crop_slc_spacetime

from caroline.config import get_config

CONFIG = get_config()
JOB_DEFINITIONS = get_config(f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False)

# Make a logger to log the stages of processing
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()  # create console handler
ch.setLevel(logging.INFO)
logger.addHandler(ch)


def get_free_port():
    """Get a non-occupied port number."""
    sock = socket.socket()
    sock.bind(("", 0))  # Bind a port, it will be busy now
    freesock = sock.getsockname()[1]  # get the port number
    sock.close()  # Free the port, so it can be used later
    return freesock


# ---- Config 1: Path Configuration ----
# Paths and files
stack_dir = Path("**coregistration_directory**/**stack_folder_name**")  # ifg stack dir
mother_dir = stack_dir / "**mother**"  # Mother image dir
reading_chunks = (4000, 4000)  # Reading chunks (azimuth, range) from binary
sensor = "**sensor**"

# Output config
overwrite_zarr = False  # Flag for zarr overwrite
writing_chunks = {"azimuth": 4000, "range": 4000, "time": 1}  # Writing chunks to zarr, (azimuth, range, time)
path_figure = Path("./figure")  # Output path for figure
path_figure.mkdir(exist_ok=True)  # Make figure directory if not exists


# ---- Config 2: Dask configuration ----

# Option 1: Initiate a new SLURMCluster
# Uncomment the following part to setup a new Dask SLURMCluster
N_WORKERS = JOB_DEFINITIONS["jobs"]["crop_to_zarr"]["bash-file"]["bash-file-slurm-cluster"][
    "slurm-cluster-n-workers"
]  # Manual input: number of workers to spin-up
FREE_SOCKET = get_free_port()  # Get a free port
cluster = SLURMCluster(
    name="dask-worker",  # Name of the Slurm job
    queue="normal",  # Name of the node partition on your SLURM system
    cores=4,  # Number of cores per worker
    memory="30 GB",  # Total amount of memory per worker
    processes=1,  # Number of Python processes per worker
    walltime=JOB_DEFINITIONS["jobs"]["crop_to_zarr"]["bash-file"]["bash-file-slurm-cluster"][
        "slurm-cluster-worker-time"
    ],  # Reserve each worker for X hour
    scheduler_options={
        "dashboard_address": f":{FREE_SOCKET}",  # Host Dashboard in a free socket
    },
)
cluster.scheduler.no_workers_timeout = 3 * 60 * 60  # If no workers are detected for 3 hours, terminate (#208)
ADDRESS = None

# logger.info(f"Dask dashboard hosted at port: {FREE_SOCKET}.")
# logger.info(
#     f"If you are forwarding Jupyter Server to a local port 8889, \
#     you can access it at: localhost:8889/proxy/{FREE_SOCKET}/status"
# )

# Option 2: Use an existing SLURMCluster by giving the schedular address
# Uncomment the following part to use an existing Dask SLURMCluster
# ADDRESS = "tcp://XX.X.X.XX:12345" # Manual input: Dask schedular address
# SOCKET = 12345 # Manual input: port number. It should be the number after ":" of ADDRESS
# cluster = None  # Keep this None, needed for an if statement
# logger.info(f"Dask dashboard hosted at port: {SOCKET}.")
# logger.info(
#     f"If you are forwarding Jupyter Server to a local port 8889, \
#     you can access it at: localhost:8889/proxy/{SOCKET}/status"
# )

if __name__ == "__main__":
    logger.info("Initializing ...")

    if cluster is None:
        # Use existing cluster
        client = Client(ADDRESS)
    else:
        # Scale a certain number workers
        # each worker will appear as a Slurm job
        cluster.scale(jobs=N_WORKERS)
        client = Client(cluster)

    logger.info("Loading data ...")
    # Metadata
    f_mother_res = mother_dir / "slave.res"

    if sensor.upper() == "S1":
        metadata = read_metadata(f_mother_res)  # Only works for Doris v5 output

    else:
        f = open(f_mother_res)
        data = f.read()
        f.close()
        # -500 due to the resampling step subtracting 500 pixels in azimuth and range
        metadata = {
            "n_lines": eval(data.split("Number of lines (non-multilooked): \t\t")[1].split("\n")[0]) - 500,
            "n_pixels": eval(data.split("Number of pixels (non-multilooked): \t\t")[1].split("\n")[0]) - 500,
        }

    # Coordinates
    f_lam = mother_dir / "lam.raw"  # lon
    f_phi = mother_dir / "phi.raw"  # lat

    # Mother SLC
    f_mother_slc = mother_dir / "**mother_slc_name**"

    # List of SLC
    f_ifgs = list(sorted(stack_dir.rglob("2*/cint_srd.raw")))
    f_h2phs = list(sorted(stack_dir.rglob("2*/h2ph_srd.raw")))

    shape = (metadata["n_lines"], metadata["n_pixels"])

    dtype_slc_ifg = np.dtype([("re", np.float32), ("im", np.float32)])
    dtype_lam_phi = np.float32

    # Lazy loading ifg stack
    ifgs = sarxarray.from_binary(f_ifgs, shape, dtype=dtype_slc_ifg, chunks=reading_chunks)  # Load ifgs
    ifgs_h2ph = sarxarray.from_binary(
        f_h2phs, shape, vlabel="h2ph", dtype=dtype_lam_phi, chunks=reading_chunks
    )  # Load h2phs
    ifgs = ifgs.assign({"h2ph": ifgs_h2ph["h2ph"].astype(np.float32)})  # Add h2ph to ifgs
    ifgs["time"] = [datetime.strptime(file.parts[-2], "%Y%m%d") for file in f_ifgs]  # Add time coords to ifgs

    # Lazy loading mother SLC
    mother = sarxarray.from_binary([f_mother_slc], shape, dtype=dtype_slc_ifg, chunks=reading_chunks)  # Load mother SLC
    # Construct a dummy h2ph with zeros and assign to mother
    mother_h2ph = mother["amplitude"].copy()
    mother_h2ph.data = da.zeros(mother_h2ph.shape, dtype=np.float32)
    mother = mother.assign({"h2ph": mother_h2ph})
    # Add time coords to mother
    mother["time"] = [datetime.strptime(f_mother_slc.parts[-2], "%Y%m%d")]

    # Generate reconstructed SLCs
    slc_recon = ifg_to_slc(mother, ifgs)

    # Extract real and image part. remove other fields. convert to float16
    # This applies to both slc_recon and mother
    slc_recon_output = slc_recon.copy()
    slc_mother = mother.copy()
    slc_recon_output = slc_recon_output.assign(
        {
            "real": slc_recon_output["complex"].real.astype(np.float16),
            "imag": slc_recon_output["complex"].imag.astype(np.float16),
        }
    )
    slc_mother = slc_mother.assign(
        {
            "real": mother["complex"].real.astype(np.float16),
            "imag": mother["complex"].imag.astype(np.float16),
        }
    )
    slc_recon_output = slc_recon_output.drop_vars(["complex", "amplitude", "phase"])
    slc_mother = slc_mother.drop_vars(["complex", "amplitude", "phase"])

    # Add mother SLC to the output
    slcs_output = (
        xr.concat([slc_recon_output, slc_mother], dim="time").drop_duplicates(dim="time", keep="last").sortby("time")
    )

    # Add geo-ref coords
    lon = sarxarray.from_binary([f_lam], shape, vlabel="lon", dtype=dtype_lam_phi, chunks=reading_chunks).isel(time=0)[
        "lon"
    ]
    lat = sarxarray.from_binary([f_phi], shape, vlabel="lat", dtype=dtype_lam_phi, chunks=reading_chunks).isel(time=0)[
        "lat"
    ]
    slcs_output = slcs_output.assign({"lon": lon, "lat": lat})

    slcs_output = crop_slc_spacetime(slcs_output, aoi_filename="**shape_directory**/**shape_AoI_name**_shape.shp")
    # Rechunk and write as zarr
    slcs_output = slcs_output.chunk(writing_chunks)
    if not os.path.exists("**crop_to_zarr_output_filename**.zarr"):
        slcs_output.to_zarr("**crop_to_zarr_output_filename**.zarr", mode="w")
    else:
        slcs_output.to_zarr("**crop_to_zarr_output_filename**.zarr", mode="w")

    logger.info("Finishing... Closing client.")
    # Close the client when finishing
    client.close()
