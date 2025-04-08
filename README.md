# README

Welcome to the CAROLINE Project source code repository.

CAROLINE (Contextual and Autonomous processing of satellite Radar Observations for Learning and Interpreting the Natural and built Environment)  is an InSAR data processing system that automates the InSAR processing chain from download to final output. It allows for continuous product generation, where predefined products are created as new datasets are downloaded, as wel as ad-hoc product creation.

The current documentation still mostly pertains to v0.1.0. In v2.0.0, the continuous and ad hoc product generation is functional, but the database integration with docker-compose.yml is still missing. 

**Table of Contents**

- [Terminology](#terminology)
- [The way it works: cron](#the-way-it-works-cron)
- [Installation on Spider](#installation-on-spider)
    - [Installing for the first time](#installing-for-the-first-time)
    - [Updating the installation](#updating-the-installation)
- [Development without dockers](#development-without-dockers)
  - [Local Installation Guide](#local-installation-guide)
  - [Linting and formatting](#linting-and-formatting)
  - [Testing](#testing)
  - [Documentation](#documentation)
- [Development using dockers (not integrated yet)](#development-using-dockers-not-integrated-yet)
  - [Container usage](#container-usage)
    - [.env file](#env-file)
    - [caroline](#caroline)
    - [caroline-dev](#caroline-dev)
    - [caroline-db](#caroline-db)
- [Contacts](#contacts)
  - [Project Lead](#project-lead)
  - [Developers](#developers)
  - [Repository admins](#repository-admins)

# Terminology
- A <b>module</b> is a block in the CAROLINE architecture. An example is the <i>autonomous stack building</i> module. A module has one or more submodules.
- A <b>submodule</b> is a component of a module. An example is <i>coregistration</i>, part of the <i>autonomous stack building</i> module. A submodule has one or more jobs.
- A <b>job</b> is a single program that achieves a clearly specified goal, that is individually submitted to the SLURM manager. The <i>coregistration</i> submodule contains three jobs: <i>Doris v5</i> (Sentinel-1 coregistration), <i>Doris v5 cleanup</i>, and <i>DeInSAR</i> (for coregistration of other sensors). A job consists of exactly one function call to a preparation function, and optionally one bash script to be executed.
- A <b>function</b> is a Python function.


# The way it works: cron
A cron job is a job that starts at a regular interval. On Spider, these can be managed with the commands `crontab -l` (for viewing the current crontab) and `crontab -e` (for editing the crontab). A cron job looks like
```commandline
0   */5 *   *   *     bash /absolute/path/to/script.sh  
```
- The first (`0`) indicates the minute of the hour, in this case exactly at the hour.
- The second (`*/5`) is the hour marker: every hour that is evenly divisible by 5 (so every 5 hours).
- The third field (`*`) is the day of the month, in this case every day.
- The fourth field (`*`) is the month, in this case every month.
- The fifth field (`*`) is the day of the week, in this case every day.


CAROLINE runs using four cron jobs as shown in `templates/cron/caroline-admin-spider.crontab`:


```cron
CAROLINE=/project/caroline/Software/caroline
0   */5 *   *   *     bash ${CAROLINE}/scripts/run-caroline.sh  # every 5 hours
0   *   *   *   *     bash ${CAROLINE}/scripts/manage-portal-upload.sh  # every hour
0   2   *   *   *     bash ${CAROLINE}/scripts/create-overview-kml.sh  # every day at 2 am
0   1   *   *   *     bash ${CAROLINE}/scripts/email-log.sh  # every day at 1 am
```
- The first script, `run-caroline.sh`, checks for new downloads every 5 hours and starts the corresponding workflows as defined in the `config` directory.
- The second script, `manage-portal-upload.sh`, checks every hour if new jobs are ready to be pushed to the portal.
- The third script, `create-overview-kml.sh`, creates an overview of all available data on Spider at 2am every night.
- The fourth script, `email-log.sh`, sends an email to an admin account at 1am every night containing everything that happened the previous day.

On Spider, the crontab is installed on `ui-01` on the `caroline-admin` account.

# Installation on Spider

### Installing for the first time

CAROLINE is intended to be installed on a server with a SLURM manager, such as SURFSara Spider. To install on Spider, first we need to prepare the virtual environment in the directory specified in `caroline.config`. To do so, run
```bash
cd /path/to/the/virtual/environment/without/the/last/caroline/directory
source /project/caroline/Software/bin/init.sh  # loads the module command
module load python/3.10.4  # loads the correct python environment
python3 -m venv caroline  # create the virtual environment
```

Now, we are ready to install CAROLINE. First, clone the repository anywhere on Spider, and run
```bash
cd caroline
./spider-install.sh
```

The installation script takes care of generating all necessary directories and updating the created virtual environment.

### Updating the installation
To update the installation of CAROLINE, go to the directory where you originally cloned the repository. Then run
```bash
cd caroline
git pull
./spider-install.sh
```

This will store the existing configuration, and update all files, dependencies, and the virtual environment. Already running jobs are unaffected, but the changes will immediately take effect on newly starting jobs (both newly submitted and those already in the queue that have not yet started).

# Development without dockers
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

## Testing

Under development

## Documentation

We use `mkdocs` for documentation. 

To check the documentation at local, use the following command in the root directory of the repository:

```bash
mkdocs serve
```

This will build and render the documentation at a local server. Follow the link provided in the terminal to view the documentation in the browser.


# Development using dockers (not integrated yet)

For development purposes containers have been created with the latest stable Python and PostgreSQL versions, along with a docker-compose.yml file. All developed code must be able to run in these environments.

Currently, there are 3 services defined within docker-compose.yml:
<dl>
  <dt>caroline</dt>
  <dd>In this container, caroline is installed as a package from source. You can use this container to use/test/interact with caroline.</dd>
  <dt>caroline-dev</dt>
  <dd>In this container, caroline is installed in <a href="https://setuptools.readthedocs.io/en/latest/userguide/development_mode.html">'Development Mode'</a> in ~caroline/src/caroline.</dd>
  <dt>caroline-db</dt>
  <dd>The caroline database: a PostgreSQL database container with PostGIS extensions installed.</dd>
</dl>

## Container usage

### .env file

Before starting any containers, you must setup a .env file. An example .env file is provided in .env.example.

Copy the example .env file:
```text
$ cp .env.example .env
```

The defaults should be OK for development purposes. Do not use these settings in production. Review the file and make any desired changes.

### caroline

This container has caroline installed as a package so it can be interacted with as intended in a normal installation. It can be used for interactive testing of the installed package.

Starting the container:
```text
$ docker-compose up -d --build caroline
```

The database container is automatically started as a dependency.

Interacting with the container:
```text
$ docker exec -it --user caroline caroline bash
caroline@caroline:~$
```

You can now use caroline:
```text
caroline@caroline:~$ caroline --version
CAROLINE v0.1.0

Database       : PostgreSQL 13.3 (Debian 13.3-1.pgdg100+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 8.3.0-6) 8.3.0, 64-bit
PostGIS        : 3.1 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
PostGIS Full   : POSTGIS="3.1.2 cbe925d" [EXTENSION] PGSQL="130" GEOS="3.7.1-CAPI-1.11.1 27a5e771" PROJ="Rel. 5.2.0, September 15th, 2018" LIBXML="2.9.4" LIBJSON="0.12.1" LIBPROTOBUF="1.3.1" WAGYU="0.5.0 (Internal)"
PostGIS GEOS   : 3.7.1-CAPI-1.11.1 27a5e771
PostGIS Lib    : 3.1.2
PostGIS LibXML : 2.9.4
PostGIS PROJ   : Rel. 5.2.0, September 15th, 2018

```

### caroline-dev

This container has caroline installed in <a href="https://setuptools.readthedocs.io/en/latest/userguide/development_mode.html">'Development Mode'</a> in ~caroline/src/caroline. If you're not familiar with setuptools' development mode you can read up on it here: <a href="https://setuptools.readthedocs.io/en/latest/userguide/development_mode.html">https://setuptools.readthedocs.io/en/latest/userguide/development_mode.html</a>. A short description: Having to build and install every time you make a change to the code is laborious. With development mode you can use the code in place while developing it without rebuilding and reinstalling the package.

Another feature of this container is that it has the PostgreSQL client psql installed. This makes for easy command line interaction with the database while developing.

Starting the container:
```text
$ docker-compose up -d --build caroline-dev
```

The database container is autmatically started as a dependency

Interacting with the container:
```text
$ docker exec -it --user caroline caroline-dev bash
caroline@caroline-dev:~$
```

Using caroline in development mode:
```text
caroline@caroline-dev:~$ cd src/caroline
caroline@caroline-dev:~/src/caroline$ caroline/caroline --version
CAROLINE v0.1.0

Database       : PostgreSQL 13.3 (Debian 13.3-1.pgdg100+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 8.3.0-6) 8.3.0, 64-bit
PostGIS        : 3.1 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
PostGIS Full   : POSTGIS="3.1.2 cbe925d" [EXTENSION] PGSQL="130" GEOS="3.7.1-CAPI-1.11.1 27a5e771" PROJ="Rel. 5.2.0, September 15th, 2018" LIBXML="2.9.4" LIBJSON="0.12.1" LIBPROTOBUF="1.3.1" WAGYU="0.5.0 (Internal)"
PostGIS GEOS   : 3.7.1-CAPI-1.11.1 27a5e771
PostGIS Lib    : 3.1.2
PostGIS LibXML : 2.9.4
PostGIS PROJ   : Rel. 5.2.0, September 15th, 2018

```

Using psql:
```text
caroline@caroline-dev:~$ psql
psql (13.3 (Debian 13.3-1.pgdg100+1))
Type "help" for help.

caroline=> select version();
                                                     version
------------------------------------------------------------------------------------------------------------------
 PostgreSQL 13.3 (Debian 13.3-1.pgdg100+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 8.3.0-6) 8.3.0, 64-bit
(1 row)

caroline=>
```

### caroline-db

The database container is normally started as a dependency by the other containers. If needed you can individually start the database:
```text
$ docker-compose up -d caroline-db
```

Interact with the database as super user:
```text
$ docker exec -it --user postgres caroline-db bash
postgres@caroline-db:/$ psql
psql (13.3 (Debian 13.3-1.pgdg100+1))
Type "help" for help.

postgres=# select version();
                                                     version
------------------------------------------------------------------------------------------------------------------
 PostgreSQL 13.3 (Debian 13.3-1.pgdg100+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 8.3.0-6) 8.3.0, 64-bit
(1 row)

postgres=#

```



# Contacts

## Project Lead

- Freek van Leijen <F.J.vanLeijen@tudelft.nl>

## Developers

- Freek van Leijen <F.J.vanLeijen@tudelft.nl>
- Simon van Diepen <S.A.N.vanDiepen@tudelft.nl>
- Niels Jansen <N.H.Jansen@tudelft.nl>

## Repository admins

- Simon van Diepen <S.A.N.vanDiepen@tudelft.nl>
- Niels Jansen <N.H.Jansen@tudelft.nl>

