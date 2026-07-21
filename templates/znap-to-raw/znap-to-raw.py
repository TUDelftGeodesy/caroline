import datetime as dt
import glob
import logging
import os
import socket

import numpy as np
import sarxarray as sxr
from dask.distributed import Client
from dask_jobqueue import SLURMCluster
from depsi.utils import crop_slc_spacetime

from caroline.config import get_config
from caroline.io import write_run_file

CONFIG = get_config()
JOB_DEFINITIONS = get_config(f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False)
SPEED_OF_LIGHT = 299_792_458  # m/s

logger = logging.getLogger(__name__)

znap_output_path = "**snap-output-path**"
raw_output_path = "**raw-output-path**/cropped_stack"
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
N_WORKERS = JOB_DEFINITIONS["jobs"]["znap_to_raw"]["bash-file"]["bash-file-slurm-cluster"][
    "slurm-cluster-n-workers"
]  # Manual input: number of workers to spin-up
FREE_SOCKET = get_free_port()  # Get a free port
cluster = SLURMCluster(
    name="dask-worker",  # Name of the Slurm job
    queue="normal",  # Name of the node partition on your SLURM system
    cores=4,  # Number of cores per worker
    memory="30 GB",  # Total amount of memory per worker
    processes=1,  # Number of Python processes per worker
    walltime=JOB_DEFINITIONS["jobs"]["znap_to_raw"]["bash-file"]["bash-file-slurm-cluster"][
        "slurm-cluster-worker-time"
    ],  # Reserve each worker for X hour
    scheduler_options={
        "dashboard_address": f":{FREE_SOCKET}",  # Host Dashboard in a free socket
    },
)
cluster.scheduler.no_workers_timeout = 3 * 60 * 60  # If no workers are detected for 3 hours, terminate (#208)

cluster.scale(jobs=N_WORKERS)
client = Client(cluster)

# continue with the actual computations
logger.info("Reading data...")
znaps = glob.glob(f"{znap_output_path}/*-coreg.znap")

data = sxr.from_znap(znaps)
data = data.rename({"latitude": "lat", "longitude": "lon"})

cropped_data = crop_slc_spacetime(data, aoi_filename=aoi_path)

timestamps = [np.datetime_as_string(epoch, unit="D").replace("-", "") for epoch in data.time.values]
mother_idx = timestamps.index(cropped_data.mother_epoch)

logger.info("Computing interferograms...")
mother_slc = cropped_data.complex.isel(time=mother_idx).data
mother_slc = mother_slc.reshape(*mother_slc.shape, 1)

cropped_data = cropped_data.assign({"complex_ifg": cropped_data.complex * np.conj(mother_slc)})

# initialize for text file writing
slcs = []
ifgs = []

# force the expected datatypes
for layer in ["lat", "lon", "h2ph", "elevation"]:
    cropped_data[layer].data = cropped_data[layer].data.astype(np.float32)
for layer in ["complex", "complex_ifg"]:
    cropped_data[layer].data = cropped_data[layer].data.astype(np.complex64)

for i in range(len(data.time.values)):
    timestamp = timestamps[i]

    write_path = f"{raw_output_path}/{timestamp}"
    os.makedirs(write_path, exist_ok=True)

    epoch_data = cropped_data.isel(time=i)
    if i == mother_idx:
        files = {
            "lam.raw": "lon",
            "phi.raw": "lat",
            "dem_radar.raw": "elevation",
            "slc_srd.raw": "complex",
            "h2ph.raw": "h2ph",
        }
    else:
        files = {
            "slc_srd.raw": "complex",
            "h2ph.raw": "h2ph",
            "cint_srd.raw": "complex_ifg",
        }
        ifgs.append(f"{timestamps[mother_idx]} {timestamp} {write_path}/cint_srd.raw")

    slcs.append(f"{timestamp} {write_path}/slc_srd.raw")

    for file in files.keys():
        if not os.path.exists(f"{write_path}/{file}"):
            logger.info(f"Writing {write_path}/{file}...")
            sxr.to_binary(
                output_path=f"{write_path}/{file}", data=epoch_data, data_var_name=files[file], allow_overwrite=False
            )
    if i == mother_idx:
        if not os.path.exists(f"{write_path}/master.res"):
            first_pixel_az_time = dt.datetime.strptime(
                str(data.metadata_mother["first_azimuth_time"]), "%Y-%m-%dT%H:%M:%S.%f000"
            )
            orbit_grid_pattern = (
                "{timestamp_s:>6}   {x_pos_18_chars:<18}   {y_pos_18_chars:<18}   {z_pos_18_chars:<18}   \n"
            )
            orbit_grid = ""
            for orb_ep in range(cropped_data.metadata_mother["orbit_time"].shape[0]):
                orbit_grid += orbit_grid_pattern.format(
                    timestamp_s=str(round(cropped_data.metadata_mother["orbit_time"][orb_ep][0]) % 86400),
                    x_pos_18_chars=str(cropped_data.metadata_mother["orbit_position"][orb_ep][0])[:18],
                    y_pos_18_chars=str(cropped_data.metadata_mother["orbit_position"][orb_ep][1])[:18],
                    z_pos_18_chars=str(cropped_data.metadata_mother["orbit_position"][orb_ep][2])[:18],
                )
            orbit_grid = orbit_grid.strip("\n")

            write_run_file(
                save_path=f"{write_path}/master.res",
                template_path=f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/templates/znap-to-raw/master.res",
                asc_dsc=None,
                track=None,
                parameter_file=None,
                other_parameters={
                    "asc_dsc": cropped_data.metadata_mother["pass_direction"].lower().capitalize(),
                    "n_az_pixels": len(cropped_data.azimuth.values),
                    "n_r_pixels": len(cropped_data.range.values),
                    "r_pixel_spacing": cropped_data.metadata_mother["range_pixel_spacing"],
                    "az_pixel_spacing": cropped_data.metadata_mother["azimuth_pixel_spacing"],
                    "radar_frequency": cropped_data.metadata_mother["radar_frequency"],
                    "centre_latitude": cropped_data.metadata_mother["scene_centre_latitude"],
                    "centre_longitude": cropped_data.metadata_mother["scene_centre_longitude"],
                    "wavelength": SPEED_OF_LIGHT / cropped_data.metadata_mother["radar_frequency"],
                    "first_pixel_az_time": first_pixel_az_time.strftime("%Y-%b-%d %H:%M:%S.%f"),
                    "PRF_hz": cropped_data.metadata_mother["pulse_repetition_frequency"],
                    "azimuth_time_interval_s": cropped_data.metadata_mother["azimuth_time_interval"],
                    "azimuth_bandwidth_hz": cropped_data.metadata_mother["total_azimuth_bandwidth"],
                    "range_2way_time_to_first_pixel_ms": cropped_data.metadata_mother["first_range_time"] * 1_000,
                    "range_sampling_rate_mhz": cropped_data.metadata_mother["range_sampling_rate"] / 1_000_000,
                    "range_bandwidth_mhz": cropped_data.metadata_mother["total_range_bandwidth"] / 1_000_000,
                    "first_range": cropped_data.range.values[0],
                    "last_range": cropped_data.range.values[-1],
                    "first_az": cropped_data.azimuth.values[0],
                    "last_az": cropped_data.azimuth.values[-1],
                    "num_data_points_orbit": cropped_data.metadata_mother["orbit_time"].shape[0],
                    "orbit_grid": orbit_grid,
                },
            )

logger.info("Writing text files...")
# the text files
SRDs = list(sorted(glob.glob(f"{raw_output_path}/*/*srd*.raw")))
ress = list(sorted(glob.glob(f"{raw_output_path}/*/*.res")))
coords = [
    f"{raw_output_path}/{cropped_data.mother_epoch}/phi.raw",
    f"{raw_output_path}/{cropped_data.mother_epoch}/lam.raw",
    f"{raw_output_path}/{cropped_data.mother_epoch}/dem_radar.raw",
]
dates = timestamps
nlines = [len(cropped_data.azimuth.values), cropped_data.azimuth.values[0], cropped_data.azimuth.values[-1]]
npixels = [len(cropped_data.range.values), cropped_data.range.values[0], cropped_data.range.values[-1]]
txt_files = {
    "dates.txt": dates,
    "nlines_crp.txt": nlines,
    "npixels_crp.txt": npixels,
    "path_coords.txt": coords,
    "path_ifgs.txt": ifgs,
    "path_images": SRDs,
    "path_res_files": ress,
    "path_slcs": slcs,
}

# write the text files
for txt_file in txt_files.keys():
    f = open(f"{raw_output_path}/{txt_file}", "w")
    for line in txt_files[txt_file]:
        f.write(f"{line}\n")
    f.close()

logger.info("Finished! Closing client...")
client.close()
