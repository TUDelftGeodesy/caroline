# CAROLINE Development

CAROLINE is a software package that is never finished. Here you can therefore read how to contribute.

- [Local Installation Guide](#local-installation-guide)
- [Linting and formatting](#linting-and-formatting)
- [Documentation](#documentation)
- [Adding a new job](#adding-a-new-job)


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

## Adding a new job

### Job architecture

Jobs are the core of CAROLINE, as they are what submodules and modules are composed of. Here we will use the `DePSI` job as an example. A job consists of one or two parts:

- A preparation function in [caroline/preparation.py](../caroline/preparation.py) called `prepare_<job>` (always)
- A bash file from [templates](../templates) (optional)

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

