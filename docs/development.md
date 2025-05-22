# CAROLINE Development

CAROLINE is a software package that is never finished. Here you can therefore read how to contribute.

- [Local Installation Guide](#local-installation-guide)
- [Linting and formatting](#linting-and-formatting)
- [Documentation](#documentation)
- [General GitHub management](#general-github-management)
- [Running tests](#running-tests)
- [Adding a new AoI](#adding-a-new-aoi)
- [Adding a new job](#adding-a-new-job)
  - [Job design](#job-design)
    - [The preparation function](#the-preparation-function)
    - [The bash file](#the-bash-file)
  - [The necessary steps for adding a job](#the-necessary-steps-for-adding-a-job)

## Local Installation Guide

It is assumed that you have `mamba` installed. If not, you can find the installation instructions [here](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html). Other package managers like `conda` or `venv` can be used as well.

On your local machine, clone the repository, and `cd` into the repository:
```bash
cd caroline
```

Create a new conda environment (here we give an example name `caroline-dev`) with `mamba`.:

```bash
mamba create -c conda-forge -n caroline-dev python=3.12
```

Here we use Python 3.12 since we aim to support python 3.10 and above.

Activate the environment:

```bash
mamba activate caroline-dev
```

Install this package in development mode, with extra dependencies for development and documentation:

```bash
pip install -e ".[dev,docs]"
```

In the end, install the pre-commit hooks, which will run the code quality checks before each commit:
```bash
pre-commit install
```
## Linting and formatting

We use `ruff` for linting and formatting. If the pre-commit hooks are installed, the checks will be run automatically before each commit.

To manually run the checks, use the following command in the root directory of the repository:

```bash
ruff check .
```

## Documentation

We use `mkdocs` for documentation. 

To check the documentation at local, use the following command in the root directory of the repository:

```bash
mkdocs serve
```

This will build and render the documentation at a local server. Follow the link provided in the terminal to view the documentation in the browser.

## General GitHub management

For any changes to the repository (including AoI changes), the following steps are performed:

1. Create an issue on https://github.com/TUDelftGeodesy/caroline/issues (if the issue already exists, this can be skipped). Make sure to add proper labels.
2. Create a branch off of the issue (on the right in the Development tab)
3. Checkout the branch in your local repository. Now you are free to change everything you want.
4. In case of changes beyond the parameter files and documentation, [test your additions in a testing environment](#running-tests).
5. Update the versioning in [pyproject.toml](../pyproject.toml). The versioning for CAROLINE consists of three numbers: `X.Y.Z` (e.g. `2.0.12`)
   1. For minor code updates (AoI changes, bugfixes, and so on): `X.Y.Z` -> `X.Y.Z+1` (e.g. `2.0.12` -> `2.0.13`)
   2. For documentation updates: `X.Y.Z` -> `X.Y.Z` (e.g. `2.0.12` -> `2.0.12`)
   3. For job additions (see [Adding a new job](#adding-a-new-job)): `X.Y.Z` -> `X.Y+1.0` (e.g. `2.0.12` -> `2.1.0`)
   4. For major architecture changes: `X.Y.Z` -> `X+1.0.0` (e.g. `2.0.12` -> `3.0.0`)
6. Update the documentation (if necessary) and [Changelog](../CHANGELOG.md) (always necessary)
7. Create a pull request, and ensure the ruff check passes.
8. Pass the code review, and merge the pull request.
9. Ask the [Admins](../README.md#contacts) to update the live installation on Spider (See [Installing on Spider](../README.md#installation-on-spider---live-version))

## Running tests
Due to the nature of Caroline, tests can generally not be done on a local installation as a SLURM-manager is required. Caroline should therefore be tested on the HPC. Before running a test, make sure you have a personal testing installation of Caroline on Spider (See [Installing on Spider - personal testing version](../README.md#installation-on-spider---personal-testing-version)).

If during your testing you need to perform updates to your local installation, follow [updating the local installation](../README.md#updating-the-installation-1).

Then, follow these steps to start a test:
1. Create an AoI you want to test on. There are two ways to do this:
   1. Add a new parameter file to the codebase intended for testing, for an example see [this parameter file](../config/parameter-files/param_file_TEST_nl_amsterdam.txt).
   2. Modify an existing parameter file. If you take this route, pay close attention to these things:
      1. Make sure to move all processing directories away from the live version to your personal directories.
      2. Make sure to update the `send_completion_email` field to only send emails to yourself (and optionally an admin)
      3. Updating the installation will remove your modifications.
2. (This assumes you followed the steps on [Installing on Spider - personal testing version](../README.md#installation-on-spider---personal-testing-version)) run the following command to go to the `work` directory:
```bash
cd /project/caroline/Share/users/$(whoami)/caroline-test/run/caroline/work
```
3. Add the AoI and track you want to test on to the force-starting AoIs by following the steps in [force-starting an AoI](management.md#force-starting-an-aoi).
4. Run
```bash
cd /project/caroline/Share/users/$(whoami)/caroline-test/caroline/scripts
bash run-caroline.sh
```
Once this command completes, your jobs are visible using the command `squeue --me`. You will receive an email when all jobs have finished with links to the log files. If you want to push layers to a portal, please ensure to add the portal manager cronjob to your [crontab](../README.md#the-way-it-works-cron).

## Adding a new AoI

1. Following the [general GitHub management](#general-github-management) steps 1-3: create an issue and a branch, and check it out locally. 
2. Copy [config/parameter-files/param_file_nl_amsterdam.txt](../config/parameter-files/param_file_nl_amsterdam.txt) into the same directory with the name `param_file_<2-letter-country-ID>_<region-name>.txt`.
3. Decide on the exact AoI. There are two options for this:
   1. Generate a rectangular AoI by following the instructions around line 57 in the parameter file.
   2. Generate your own AoI as a shapefile:
      1. In Google Earth, draw the polygon of the AoI
      2. Save the polygon as `.kmz`
      3. Using https://mygeodata.cloud/converter/kmz-to-shp , convert the `.kmz` to `.shp`, leaving all parameters unaltered. The output is a ZIP file containing five files with extensions `.cpg`, `.dbf`, `.prj`, `.shp`, `.shx`. 
      4. Upload the five files in the folder to Spider in a location you can remember using the command `scp -i /path/to/your/ssh/key /path/to/your/unzipped/shp/file/<shapefile_name>.* caroline-<user>@spider.surfsara.nl:/project/caroline/Share/path/to/your/storage/location`. The `.*` should copy all five files to this location. Fill the full path to the `.shp` file in in the `shapefile_name` field
4. Modify the parameters in the parameter file to your needs, see [parameter-file.md](parameter-file.md) for an explanation on all parameters. Pay special attention to:
   - All parameters in the `General` section (Sentinel-1 tracks will be automatically detected but can be force-included or force-excluded, for other sensors all tracks need to be specified)
   - The DEM, especially if not processing in the Netherlands. If no DEM is available in your AoI, follow the steps in [#67](https://github.com/TUDelftGeodesy/caroline/issues/67) to generate the DEM (just the DEM part) (NOTE: with [#248](https://github.com/TUDelftGeodesy/caroline/issues/248) the DEM generation will be deprecated).
   - Note that stacks are all stored in `/project/caroline/Share/stacks`, crops in `/project/caroline/Share/crops`, zarr stacks in `/project/caroline/Share/stacks_zarr`, DePSI runs in `/project/caroline/Share/projects/<country_code>_<region_of_interest>/depsi`, and shapefiles in `/project/caroline/Software/roi/<first step that will be run out of stacks / crops / depsi>/<country_code>_<region_of_interest>` for consistency.
5. Follow steps 5-9 of the [general GitHub management](#general-github-management). Once complete, your new AoI will be live.

A few notes:
- If you included the `s1_download` step in your processing, the download parameters will be automatically generated during the installation on Spider. The following logic is then automatically followed:
  - The periodic download in [manage-s1-download.sh](../scripts/manage-s1-download.sh) will during its next call download the last month of data on the tracks that were detected
  - [run-caroline.sh](../scripts/run-caroline.sh) will detect the new SLC zip files and start your new AoI
  - The first job that is run is `s1_download`, which will per track download all SLC zip files in the period you specified before continuing to coregistration.
- If `s1_download` is the _only_ step that is run, no `area-track-list` is generated and the AoI will never be started by [run-caroline.sh](../scripts/run-caroline.sh), as it is assumed this AoI is only to trigger the periodic download (e.g. the `be_lu_nl_benelux` AoI).
- Download configurations are removed when an AoI is [deactivated](management.md#activating--deactivating-an-aoi).
## Adding a new job


### Job design

Jobs are the core of CAROLINE, as they are what submodules and modules are composed of. Here we will use the `DePSI` job as an example. A job consists of one or two parts:

- A preparation function in [caroline/preparation.py](../caroline/preparation.py) called `prepare_<job>` (always)
- A bash file from [templates](../templates) (optional)

All jobs are started using [scripts/start_job.sh](../scripts/start_job.sh), which takes 5 required arguments and 2 optional arguments:
1. the parameter file (full path)
2. the track (integer)
3. the job type (e.g. `depsi`)
4. the CAROLINE installation directory
5. the CAROLINE virtual environment directory
6. (optional) the directory in which the bash file is located
7. (optional) the name of the bash file (without the full path)

If 5 arguments are passed, only the preparation function is run. If all 8 are passed, the preparation function is run, and then the bash file. All of this is handled by the [scheduler](../caroline/scheduler.py). 

#### The preparation function

This function should do everything necessary to be able to start the job. This can include

- generating directories
- setting up the files necessary to run the bash file by filling in the templates
- linking necessary output from previous steps

The preparation function always takes exactly two arguments:

- the parameter file (as an absolute path)
- the track (as an integer) or tracks (as a list of integers) to do

For example, the function `prepare_depsi` does the following:

- It moves the previous DePSI run (if present) (as this is PSI batch)
- It generates the directory
- It copies the plugins necessary from the plugins directory
- It links the mother image and DEM
- It identifies the start, mother, and end dates corresponding to the settings
- It determines the values for a few parameters that have multiple options in the parameter file and cannot be directly copied
- It writes the files necessary for running DePSI (including the bash file)
- It writes the directory contents to a file

With all these steps, DePSI can then be started from a single bash file call.

#### The bash file

The bash file is an optional file that loads the necessary environments (e.g. matlab), and then starts the processing. For example, the depsi template contains the two commands

```commandline
module --ignore-cache load matlab/R2021b

srun matlab -nodisplay -nosplash -nodesktop -r "run('**depsi_base_directory**/psi/depsi.m');exit;" || exit 5
```

The first line loads the Matlab environment (on Spider this is called a module), the second starts the Matlab processing. Important to note is the ` || exit 5` appendix: this will ensure the bash script actually stops if an error is encountered in Matlab.

In some cases (e.g. the job `email`) there is no processing to be done. In this case the bash file is not passed, and not called upon.

###  The necessary steps for adding a job

In order to fully integrate a new job into CAROLINE, the following steps need to be undertaken (we will use `DePSI` as an example)

1. Define the job name (fully lowercase without dashes, underscores are allowed). In our example case: `depsi`
2. In [config/job-definitions.yaml](../config/job-definitions.yaml), add an entry for the job formatted as follows:
   1. Add the job name in between the jobs between which the job should appear in the email, one tab in. All other keys will be one tab in from this key (so two total)
   2. Add the necessary keys (one tab in) (leaving empty will set the value to `None`:
      1. `requirement`: the name (`str`) or names (`list` of `str`) of the job that should finish before this job should start
      2. `two-letter-id`: the two letter ID that will show up in the `squeue`
      3. `partition`: either `short` (10 hours), `normal` (5 days), `infinite` (12 days), or user-specified (e.g. for `depsi`, `depsi_partition` will search for this name in the parameter file)
      4. `parameter-file-step-key`: the key in the general section of the parameter file that should be `1` for this job to run. For `depsi`, this is `do_depsi`
      5. `sbatch-args`: the arguments to pass on to `sbatch`. If no clear requirements are present, use `"--qos=long --ntasks=1 --cpus-per-task=1 --mem-per-cpu=8000"`, the most default one
      6. `directory-contents-file-appendix`: if multiple jobs run in the same directory, this appendix can be used to separate them. (e.g. for `depsi` this is `""`, for `depsi_post`, this is `_depsi_post`)
      7. `email`: always has two keys:
         1. `include-in-email`: if `True` (without quotes), the job will show up in the email. If `False`, it will not show up.
         2. `status-file-search-key`: the search key for the job resfile. For `depsi`, this is `"*resfile.txt"`, as this is where the results of the job are stored. If left empty, it is assumed no such status file exists.
      8. `bash-file`: if no bash file is to be run, leave it empty like in the `email` job. Otherwise, move one tab in, and add three keys:
         1. `bash-file-name`: the name of the bash file to be run.
         2. `bash-file-base-directory`: the name of the base directory in which the job should be run. For `depsi` this is `depsi`, which then assumes `depsi_directory` and `depsi_AoI_name` exist as parameters in the parameter file.
         3. `bash-file-directory-appendix`: a folder to add to the base directory name. In case of `depsi`, this is `/psi`, since DePSI runs in the `psi` folder within the base directory of `depsi`. If it should be empty, leave it to `""`.
      9. `filters`: in case the job should only run if specific conditions are met, these can be specified here. If left empty, it will assume no filters are present and any parameter file can start this job. If a filter (e.g. satellite) is present, use the following syntax:
         1. one tab in, add `<parameter-file-key>: <allowed-value(s)>`. `<allowed-value(s)>` can be either a `str` or `list` of `str`. If the value of the specified key in the parameter file is in the provided allowed values, the job will start. Otherwise, the job will not be scheduled.
         2. If multiple filters are necessary, add the next filter using the same syntax on a new line. The job will only start if _all_ filters are satisfied.
3. Add the two letter job ID to [abbreviations.md](abbreviations.md)
4. In [preparation.py](../caroline/preparation.py), create the function `prepare_<jobname>` that takes exactly two arguments: 
    
    ```python
    def prepare_<jobname>(parameter_file: str, do_track: int | list | None = None) -> None:
        pass
    ```
    
    this function does everything necessary to be able to complete the job with a single bash file call (or completely finishes the job if no bash file is necessary). See [The preparation function](#the-preparation-function) for an example. In our example, the function would be called `prepare_depsi`. If files need to be generated for the completion of the job:
   1. In [templates](../templates), create a new folder named `jobname`.
   2. In this folder, create a template for each file that needs to be generated. Variables that need to be replaced can be indicated with `**variable_name**`.
   3. In your preparation function, call `write_run_file` from [io.py](../caroline/io.py) with all the parameters that need to be replaced. Here three flavours exist:
      1. parameter file parameters. These are read directly from the parameter file, with optional formatting (see the documentation of `write_run_file` in [io.py](../caroline/io.py))
      2. config parameters. These are read directly from the configuration in e.g. [spider-config.yaml](../config/spider-config.yaml)
      3. other parameters. These can be anything, as you provide the value in the argument.
   
5. If the job is dependent on a plugin, add this plugin in [config/plugin-definitions.yaml](../config/plugin-definitions.yaml). If the plugin is a GitHub or bitbucket repository, add it to the `github` group with the `repo` variable (the git clone link), and a `branch` or `tag` variable (depending on whether you want to clone off of a branch or tag). If the plugin is a tarball, add it to `tarball` group.
6. If the job is dependent on a Python plugin that requires packages not yet provided in the CAROLINE virtual environment, update the `plugins` dependency list on line 50 of [pyproject.toml](../pyproject.toml) with a comment on which plugin it is necessary for.
7. If scripts are needed for the completion of the job that are not provided in the plugin, add them in [scripts](../scripts) 
8. In <b><u>all</u></b> parameter files in [config/parameter-files](../config/parameter-files), add the necessary job-specific parameters for the job in a new section.
9. If in step 2 you introduced new values for `parameter-file-step-key` and `bash-file-base-directory`: in <b><u>all</u></b> parameter files in [config/parameter-files](../config/parameter-files), add the following general parameters:
   1. `do_<parameter-file-step-key>`, a 0/1 boolean switch whether or not to execute the job. Leave to 0 for all jobs you do not want this to run on.
   2. `<bash-file-base-directory>_AoI_name`, the name of the AoI in that job
   3. `<bash-file-base-directory>_directory`, the directory in which the job should run
10. Update the version on line 7 of [pyproject.toml](../pyproject.toml) from `X.Y.Z` to `X.Y+1.0` (e.g. `2.0.12` to `2.1.0`)
11. Update the [changelog](../CHANGELOG.md) with the new version
12. Update the documentation (at the very least [architecture.md](architecture.md) and the [glossary](glossary.md), likely more)
