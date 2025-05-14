# CAROLINE Glossary



## CAROLINE Architecture
- <b>module</b>: a block in the CAROLINE [architecture](architecture.md). An example is the <i>autonomous stack building</i> module. A module has one or more submodules.
- <b>submodule</b>: a component of a module. An example is <i>coregistration</i>, part of the <i>autonomous stack building</i> module. A submodule has one or more jobs.
- <b>job</b>: a single program that achieves a clearly specified goal, that is individually submitted to the SLURM manager. The <i>coregistration</i> submodule contains three jobs: <i>Doris v5</i> (Sentinel-1 coregistration), <i>Doris v5 cleanup</i>, and <i>DeInSAR</i> (for coregistration of other sensors). A job consists of exactly one function call to a preparation function, and optionally one bash script to be executed.
- <b>function</b>: a Python function.
- <b>plugin</b>: an external software package that is called by CAROLINE to execute a job. An example is the <i>Doris v5.0.4</i> plugin, used in the job <i>Doris v5</i> in the coregistration submodule.
- <b>patch</b>: an amendment to a plugin, where the original plugin code does not function as intended for CAROLINE. All patches are located in the `patches` directory, using the exact same folder structure as will be generated in the directory read from the `CAROLINE_PLUGINS_DIRECTORY` setting.
- <b>workflow</b>: the string of consecutive jobs required to reach a specific outcome. E.g., for a psi_batch portal layer starting from a coregistered stack, the workflow is crop_to_raw > DePSI > read mrm > DePSI_post > portal upload

## HPC Functionality
- <b>HPC</b>: High-Performance Cluster, colloquially known as a supercomputer
- <b>Compute node</b>: a processor specifically intended for larger computations, on which all CAROLINE jobs are run
- <b>Login node</b>: a processor on which users can interact with the file systems of an HPC, and on which cronjobs will run
- <b>SLURM manager</b>: the compute load manager that assigns jobs to compute nodes
- <b>squeue</b>: the list of jobs that have been submitted to the SLURM manager, and are currently running or waiting to run
- <b>cronjob</b>: a job being started at specified intervals. Cronjobs will always run on login nodes
- <b>crontab</b>: the file specifying the cronjobs

## Jobs
All jobs run on a single AoI on a single track. The following specifications will assume this.

- <b>s1_download</b>: this job checks if all raw SLCs acquired between the specified start date and end date that are available on ASF have been downloaded to the HPC. This is achieved by querying the ASF servers and downloading any missing raw SLCs.
- <b>doris</b>: this job performs Sentinel-1 coregistration
- <b>doris_cleanup</b>: this job removes excess files produced by `doris`
- <b>deinsar</b>: this job performs coregistration for all sensors except Sentinel-1. 
- <b>crop_to_raw</b>: 
- <b>crop_to_zarr</b>
- <b>depsi</b>
- <b>mrm</b>
- <b>depsi_post</b>
- <b>portal_upload</b>
- <b>email</b>
