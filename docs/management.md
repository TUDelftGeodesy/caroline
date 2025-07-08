# Management

## System requirements
- SLURM-managed HPC with at least the commands `sbatch`, `srun`, `sacct`, and `squeue`
- Linux operating system
- `/etc/profile.d/modules.sh` (for module loading)
- `/project/caroline/Software/bin/init.sh` (for module initialization)
- The modules `python/2.7.15`, `python/3.10.4`, `gdal/3.4.1-alma9`, `matlab/R2021b`
- `pip` for Python installation
- Internet access on the HPC for querying the ASF servers, GitHub, Bitbucket, and contextual data
- Valid SSH keys for GitHub and Bitbucket
- A working installation of [Doris v5.0.4](http://doris.tudelft.nl/) and [Doris v4.13.1](http://doris.tudelft.nl/)

## Activating / Deactivating an AoI
In each parameter file, at the very top there is a parameter `active`. If `1`, the parameter file is active and processed. If `0`, the parameter file is inactive and not processed. This also affect the periodic download setup. 
When changing a parameter file, do not forget to follow [the GitHub management](development.md#general-github-management).


## Force-starting an AoI
Note: dependencies across different AoIs are ignored when force-starting. Thus: submitting both `nl_veenweiden` and `nl_amsterdam` will **not** take into account the dependency of `nl_veenweiden` on `nl_amsterdam`

There are two options to force-start an AoI. 

### Option 1: commandline (for one or a few force-starts)
The first option is handy for a single force-start (or a few):
```bash
cd /path/to/your/caroline/install
cd scripts
bash run-caroline.sh "AoI_name" "track" # e.g. bash run-caroline.sh TEST_nl_amsterdam s1_dsc_t037
```

If you want to start more than one AoI, repeat the last command for each AoI (Caroline does not accept more than one at a time). If you have a lot to force-start, consider option 2:

### Option 2: force-start-runs.dat (for many force-starts)
The second option is handy for many force-starts. In the `CAROLINE_WORK_DIRECTORY` in the config file (e.g. [spider-config.yaml](../config/spider-config.yaml)), a file called `force-start-runs.dat` is present.
To force-start an AoI, add the following to the file:
```text
AoI_name;track1,track2,track3
```
E.g., to force start `nl_groningen_cubic`, Sentinel-1 track 88, and `nl_assendelft`, Sentinel-1 track 110 and track 161, add:
```text
nl_groningen_cubic;s1_asc_t088
nl_assendelft;s1_dsc_t110,s1_asc_t161
```
Each new AoI is on a new line. 





## Job logs
Each job produces output. The SLURM-output (containing all output printed to the terminal and possibly errors) are all located in the slurm output directory as defined in the configuration file (e.g. [spider-config.yaml](../config/spider-config.yaml)). 
The email will contain full-path links to these output files for each job included in said email.

Some processes also produce different types of logging themselves (e.g. `DePSI`). These files are specified in [job-definitions.yaml](../config/job-definitions.yaml), in the `status-file-search-key` field. The full path to these files, as well as the output of these status files is appended to the email.

## Fixing crashed jobs
Sometimes jobs will crash. If this happens, follow the following steps:

1. Create an [issue](https://github.com/TUDelftGeodesy/caroline/issues) detailing the crash and all logs that contain relevant information.
2. Investigate in past issues if something similar happened. If it did, follow the steps in that ticket to resolve the issue.
3. If this is a new type of issue we need to delve deeper into what is happening. Generally there are four types of crashes. We need to figure out which type of crash it is: 
   1. Faulty input data (e.g [#76](https://github.com/TUDelftGeodesy/caroline/issues/76)): in this case the issue does not lie with Caroline but rather with data it was provided. These are almost always characterized by errors coming from within calls to plugins that happen in a single AoI.
   2. Something in Caroline broke (e.g. [#77](https://github.com/TUDelftGeodesy/caroline/issues/77) or [#74](https://github.com/TUDelftGeodesy/caroline/issues/74)). These are almost always characterized by either errors coming from within the Caroline functions, or errors that affect many AoIs.
   3. Random time-out (e.g. [#107](https://github.com/TUDelftGeodesy/caroline/issues/107)): there is no clear error in the SLURM output or any other job logs, it just stopped running. In these cases running `sacct --jobs=<job_id>` (with `<job_id>` the number in the SLURM output filename) on the cluster will often say `CANCELLED`. Note: sometimes errors related to the SLURM manager are present (examples are present in [#107](https://github.com/TUDelftGeodesy/caroline/issues/107)). These also fall in this category.
   4. Something in one of the plugins broke (e.g. [#267](https://github.com/TUDelftGeodesy/caroline/issues/267)): there is a clear error in the SLURM output that originated in a plugin, but it affects many AoIs.
4. Document your findings in your issue.
5. The solution approach is different for each of these types of crashes. Note: these are general pointers, for each issue the exact solution might be slightly different.
   1. **Faulty input data**. Here the issue lies with the input, so this needs to be fixed. If it originates in the parameter file, update the parameter file (don't forget about [the GitHub management](development.md#general-github-management) and to reinstall Caroline on Spider). Note that in some cases more development might be necessary (e.g. [#68](https://github.com/TUDelftGeodesy/caroline/issues/68)). If it originates in external data (SLCs, orbits, or other), the external data needs to be replaced with working versions. One special case:
      - If your investigation finds that an SLC zip-file is broken, you can redownload it using the command `/project/caroline/Software/bin/s1-download-slc --single-product=S1A_IW_SLC__1SDV_20230930T172557_20230930T172624_050560_06170F_CE64-SLC –-redownload`. Here the zip file to be redownloaded is `/project/caroline/Data/radar_data/sentinel1/s1_asc_t088/IW_SLC__1SDV_VVVH/20230930/S1A_IW_SLC__1SDV_20230930T172557_20230930T172624_050560_06170F_CE64.zip`. The `.zip` and the directory structure are removed from the filename, and `-SLC` is appended. The SLC download will figure out which directory to place the SLC into by itself. 
   3. **Something in Caroline broke**. Here development is necessary to fix the bug(s). Follow [the GitHub management](development.md#general-github-management) to accomplish this.
   3. **Randome time-out**. Here the problem lies with Spider. Add the process that crashed to [#107](https://github.com/TUDelftGeodesy/caroline/issues/107).
   4. **A plugin broke**. The bug should be patched in the plugin, either in the repository of the plugin or by adding a patch in the [patches](../patches) directory.
6. Document your findings in your issue.
7. If you have changed something in the repository, follow [the GitHub management](development.md#general-github-management) steps. This will automatically close your issue. If not, close your issue manually.
8. Restart the job using one of these options:
   - if you downloaded a new SLC zip-file, Caroline will automatically restart
   - if an entire track crashed (e.g. all AoIs on track 161), go to the most recent image of that track (e.g. `cd /project/caroline/Data/radar_data/sentinel1/s1_asc_t161/IW_SLC__1SDV_VVVH/20250521/`). In this directory, run `touch *.json`. This will trigger the redetection, and start _all_ AoIs on this track. 
   - if you do not want to start all AoIs on a single track, the AoIs you do want to start should be [force-started](#force-starting-an-aoi).
   - waiting for a new acquisition (if it's less than a day away)



