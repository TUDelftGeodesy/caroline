# Changelog


All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## Example template!! (For the newest version, NEWHASH = main. Don't forget to update the previous versions hash too)

## [version](https://github.com/TUDelftGeodesy/caroline/tree/NEWHASH) (DD-MMM-YYYY, [diff](https://github.com/TUDelftGeodesy/caroline/compare/OLDHASH...NEWHASH))

### Added:
-

### Changed:
-

### Fixed:
- 

### Removed:
-

-->

## [v2.3.0](https://github.com/TUDelftGeodesy/caroline/tree/main) (12-May-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/f9f14bd19aab322adc28f1f552b2f8a59af23fba...main))

### Added:
- `s1_download` job
- Periodic downloads are now part of CAROLINE proper instead of its separate environment
- This changelog

### Changed:
- `nl_groningen_cubic` now runs on the same crop as `nl_groningen`
- Added the previous developers back in [README.md](README.md)
- Tracks now only trigger on new images that originate in the last 30 days, to prevent repeat triggering during the running of an `s1_download` job

### Removed:
- Deprecated `download` directory, as it is replaced by the [caroline-download](https://github.com/TUDelftGeodesy/caroline-download) package


## [v2.2.2](https://github.com/TUDelftGeodesy/caroline/tree/f9f14bd19aab322adc28f1f552b2f8a59af23fba) (07-May-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/ffe9e7556051f9432e95c5dc0ce0d2192805fed1...f9f14bd19aab322adc28f1f552b2f8a59af23fba))

### Fixed:
- `nl_groningen_cubic` now has its correct AoI


## [v2.2.1](https://github.com/TUDelftGeodesy/caroline/tree/ffe9e7556051f9432e95c5dc0ce0d2192805fed1) (06-May-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/baecc68bcbc73ba83861df7def9205d58adb3571...ffe9e7556051f9432e95c5dc0ce0d2192805fed1))

### Changed:
- If multiple reference points are present, all are specified in the output of `DePSI_post` instead of throwing an error

## [v2.2.0](https://github.com/TUDelftGeodesy/caroline/tree/baecc68bcbc73ba83861df7def9205d58adb3571) (06-May-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/aec43497e432aed5d7eb889bec93d1799ef9f5a9...baecc68bcbc73ba83861df7def9205d58adb3571))

### Added:
- Contextual data manager providing daily updates
- [Contextual data definitions](config/contextual-data-definitions.yaml)
- Designated Target Database as contextual data
- Contextual data updating during installation

### Changed:
- The default configuration file is now properly defined

## [v2.1.12](https://github.com/TUDelftGeodesy/caroline/tree/aec43497e432aed5d7eb889bec93d1799ef9f5a9) (01-May-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/c7108d9299147163ded560a6cd52473c8fed0979...aec43497e432aed5d7eb889bec93d1799ef9f5a9))

### Fixed:
- `crop-to-zarr` will now terminate if its workers have died

## [v2.1.11](https://github.com/TUDelftGeodesy/caroline/tree/c7108d9299147163ded560a6cd52473c8fed0979) (30-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/1182e39f1dd4c105568ce2a3b0224bb35a3ca4d1...c7108d9299147163ded560a6cd52473c8fed0979))

### Fixed:
- The correct index for Matlab checking in the proper finish check is now selected

## [v2.1.10](https://github.com/TUDelftGeodesy/caroline/tree/1182e39f1dd4c105568ce2a3b0224bb35a3ca4d1) (30-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/d727f159f9a9900d65cc96bdc42b91f94350597e...1182e39f1dd4c105568ce2a3b0224bb35a3ca4d1))

### Added:
- AoI `nl_groningen_cubic`

## [v2.1.9](https://github.com/TUDelftGeodesy/caroline/tree/d727f159f9a9900d65cc96bdc42b91f94350597e) (30-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/fb38928fd9a937b1a8b40f875909ff49270e130a...d727f159f9a9900d65cc96bdc42b91f94350597e))

### Fixed:
- Github plugins are now separated by branch or tag, as the commands to update both differ


## [v2.1.8](https://github.com/TUDelftGeodesy/caroline/tree/fb38928fd9a937b1a8b40f875909ff49270e130a) (29-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/fc67d3c4ef658470f3c9c22377d8168c22fff73c...fb38928fd9a937b1a8b40f875909ff49270e130a))

### Fixed:
- The directory contents file is now read properly during the proper job completion check

## [v2.1.7](https://github.com/TUDelftGeodesy/caroline/tree/fc67d3c4ef658470f3c9c22377d8168c22fff73c) (28-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/19d02c3e3ff81a2c467ce28bce0a25c625e921d4...fc67d3c4ef658470f3c9c22377d8168c22fff73c))

### Fixed:
- Generation of the directory contents now reads the correct configuration file

## [v2.1.6](https://github.com/TUDelftGeodesy/caroline/tree/19d02c3e3ff81a2c467ce28bce0a25c625e921d4) (28-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/e4cda48536bfebd6438cd3abdbaf05fdf5642808...19d02c3e3ff81a2c467ce28bce0a25c625e921d4))

### Changed:
- Emails are now managed from [job-definitions.yaml](config/job-definitions.yaml)
- The generation of the directory contents is now managed from [job-definitions.yaml](config/job-definitions.yaml)
- Proper job completion is now checked using `sacct`

### Fixed:
- Emails now have a sender and are no longer quarantined for 196 minutes

### Removed:
- Documentation of `write_run_file` is no longer specifies which configuration parameters are available

## [v2.1.5](https://github.com/TUDelftGeodesy/caroline/tree/e4cda48536bfebd6438cd3abdbaf05fdf5642808) (28-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/545e47956b06c66211ccdfa6ea92ead4927be457...e4cda48536bfebd6438cd3abdbaf05fdf5642808))

### Changed:
- The check on whether a job should be scheduled or not is now a function

## [v2.1.4](https://github.com/TUDelftGeodesy/caroline/tree/545e47956b06c66211ccdfa6ea92ead4927be457) (23-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/224921ebfbe3777455ee8eb419f5ca7ab38663bc...545e47956b06c66211ccdfa6ea92ead4927be457))

### Fixed:
- The scheduler now properly handled dependencies across different AoIs if the specified dependencies are formatted as a list

## [v2.1.3](https://github.com/TUDelftGeodesy/caroline/tree/224921ebfbe3777455ee8eb419f5ca7ab38663bc) (22-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/3611a19fe2fecc666d1d2aa43d00a511750bb8db...224921ebfbe3777455ee8eb419f5ca7ab38663bc))

### Changed:
- `crop` is now named `crop-to-raw`
- `re-SLC` is now named `crop-to-zarr`

## [v2.1.2](https://github.com/TUDelftGeodesy/caroline/tree/3611a19fe2fecc666d1d2aa43d00a511750bb8db) (22-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/1907171f50b21e6cd2168e64ebeb2367379069e1...3611a19fe2fecc666d1d2aa43d00a511750bb8db))

### Changed:
- PSP setting for `DePSI`, `nl_groningen`

## [v2.1.1](https://github.com/TUDelftGeodesy/caroline/tree/1907171f50b21e6cd2168e64ebeb2367379069e1) (17-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/d0c32d613f42dcdd63bf1365dbb010ec47ccc3f4...1907171f50b21e6cd2168e64ebeb2367379069e1))

### Added:
- The virtual environment is now created if it does not yet exist
- Explanation for how to use a local test configuration

### Removed:
- Explanation on how to make a virtual environment

## [v2.1.0](https://github.com/TUDelftGeodesy/caroline/tree/d0c32d613f42dcdd63bf1365dbb010ec47ccc3f4) (17-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/2821ba5983dcd2fca1e706520d7de7eb01f8ea6e...d0c32d613f42dcdd63bf1365dbb010ec47ccc3f4))

### Added:
- Testing environment specifications in [spider-test-config.yaml](config/spider-test-config.yaml)  
- Instructions on installing the test environment
- Filter possibility to only run jobs on AoIs where settings in the parameter file are as specified
- The configuration is now added as `installation-config.yaml` in [config](config) during the installation
- `TEST` run mode, which will not trigger `find-new-insar-files.sh`

### Changed:
- The path configuration is now read from [spider-config.yaml](config/spider-config.yaml) 
- The job configurations are now read from [job-definitions.yaml](config/job-definitions.yaml)
- The plugins are now read from [plugin-definitions.yaml](config/plugin-definitions.yaml)
- `SENDMAIL_DIRECTORY` is now named `SENDMAIL_EXECUTABLE`
- The specified dependencies are all added as dependencies to the job submission, and are filtered based on what is actually submitted
- Move plugin-related dependencies to an optional `plugins` dependency package


## [v2.0.13](https://github.com/TUDelftGeodesy/caroline/tree/2821ba5983dcd2fca1e706520d7de7eb01f8ea6e) (15-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/a1cb07fd4e7bb3637c7bf90016ec3422213386cb...2821ba5983dcd2fca1e706520d7de7eb01f8ea6e))

### Fixed:
- Formatting of the logging email used to split the logs at the wrong location

## [v2.0.12](https://github.com/TUDelftGeodesy/caroline/tree/a1cb07fd4e7bb3637c7bf90016ec3422213386cb) (15-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/4939c3b806318de8c276a6ede06ed8bcef5e903d...a1cb07fd4e7bb3637c7bf90016ec3422213386cb))

### Added:
- Definitions for `plugin` and `patch` in [README.md](README.md)
- The [development guide](docs/development.md)

### Changed:
- Processing parameters of `nl_limburg` to ease the detection of the IGRS


## [v2.0.11](https://github.com/TUDelftGeodesy/caroline/tree/4939c3b806318de8c276a6ede06ed8bcef5e903d) (14-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/e46ca07fcde22d6bf6016cb6efe776b3685a7544...4939c3b806318de8c276a6ede06ed8bcef5e903d))

### Fixed:
- f-strings do not exist in Python 2, and are now no longer used in `DeInSAR`

## [v2.0.10](https://github.com/TUDelftGeodesy/caroline/tree/e46ca07fcde22d6bf6016cb6efe776b3685a7544) (14-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/ec0aaf58798fcdb092eb6f6585099083412f7c8e...e46ca07fcde22d6bf6016cb6efe776b3685a7544))

### Fixed:
- `DeInSAR` now reads the coregistration directory instead of the crop directory

## [v2.0.9](https://github.com/TUDelftGeodesy/caroline/tree/ec0aaf58798fcdb092eb6f6585099083412f7c8e) (14-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/3fe89d2b26446a6e69508e7c1ee02a6d9606dea7...ec0aaf58798fcdb092eb6f6585099083412f7c8e))

### Fixed:
- `DeInSAR` now uses the correct Python version (Python 2.7 instead of Python 3.10)

## [v2.0.8](https://github.com/TUDelftGeodesy/caroline/tree/3fe89d2b26446a6e69508e7c1ee02a6d9606dea7) (14-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/ba0f1a2eb0cf23988d4260d30a334e1e737ff69e...3fe89d2b26446a6e69508e7c1ee02a6d9606dea7))

### Fixed:
- `DeInSAR` now uses the correct keyword when reading the shapefile extent

## [v2.0.7](https://github.com/TUDelftGeodesy/caroline/tree/ba0f1a2eb0cf23988d4260d30a334e1e737ff69e) (14-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/08200f6569ba2c051ffefe05ec06f458f6071108...ba0f1a2eb0cf23988d4260d30a334e1e737ff69e))

### Changed:
- Coregistration of `nl_north_holland_south_tsx` now runs on `infinite` partition

## [v2.0.6](https://github.com/TUDelftGeodesy/caroline/tree/08200f6569ba2c051ffefe05ec06f458f6071108) (14-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/c8158ac89e361896d4b06c349523d77f1b0703a1...08200f6569ba2c051ffefe05ec06f458f6071108))


### Fixed:
- Detection of the mother image for non-Sentinel-1 in `crop` now works regardless of `DeInSAR` version




## [v2.0.5](https://github.com/TUDelftGeodesy/caroline/tree/c8158ac89e361896d4b06c349523d77f1b0703a1) (10-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/083892b999d3bf4a0cc4612e6e60a5bf058b6725...c8158ac89e361896d4b06c349523d77f1b0703a1))

### Added
- Definition of `workflow` to [README.md](README.md)

### Fixed:
- Formatting of portal upload flags now registers newlines
- Abbreviation of `nl_veenweiden` in [abbreviations.md](docs/abbreviations.md) is now correct



## [v2.0.4](https://github.com/TUDelftGeodesy/caroline/tree/083892b999d3bf4a0cc4612e6e60a5bf058b6725) (10-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/81d4a08f7fe0671118730d5e112349f25126f2cd...083892b999d3bf4a0cc4612e6e60a5bf058b6725))

### Added
- AoI `nl_marken_tsx`

### Changed:
- `nl_groningen` now also runs `DePSI` and `DePSI_post`
- `nl_limburg` now also runs `Doris v5`

### Removed:
- AoIs `nl_groningen_depsi` and `nl_limburg_stack`

## [v2.0.3](https://github.com/TUDelftGeodesy/caroline/tree/81d4a08f7fe0671118730d5e112349f25126f2cd) (10-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/07ef9b308b0aba75f66f5c9334ed2f4ed3c430d1...81d4a08f7fe0671118730d5e112349f25126f2cd))


### Fixed:
- Finished portal upload no longer logs as `initiated`



## [v2.0.2](https://github.com/TUDelftGeodesy/caroline/tree/07ef9b308b0aba75f66f5c9334ed2f4ed3c430d1) (10-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/aba18dc3205b65f6b00664493cf46f6f2df238f3...07ef9b308b0aba75f66f5c9334ed2f4ed3c430d1))


### Fixed:
- Faulty path that caused log email to not send is corrected

## [v2.0.1](https://github.com/TUDelftGeodesy/caroline/tree/aba18dc3205b65f6b00664493cf46f6f2df238f3) (09-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/69d07113ce479922d623604e3866544bf17d4038...aba18dc3205b65f6b00664493cf46f6f2df238f3))


### Fixed:
- Email generation will only attempt to read the directory contents when the SLURM output exists



## [v2.0.0](https://github.com/TUDelftGeodesy/caroline/tree/69d07113ce479922d623604e3866544bf17d4038) (08-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/c141134e837314b9d38aa5778add312d6b0b0a4d...69d07113ce479922d623604e3866544bf17d4038))

### Added:
- Terminology definitions `module`, `submodule`, `job`, `function`
- Installation explanation
- Central configuration of paths
- Inline and function documentation
- Jobs are now submitted as dependencies to one another instead of with a `CAROLINE` manager
- Abbreviations for jobs and AoIs to show up in the `squeue`
- Abbreviation documentation in [abbreviations.md](docs/abbreviations.md)
- Plugin patches are now included in the repository
- Ability to specify partitions for some jobs

### Changed:
- All functionality is moved from the prototype directory into [caroline](caroline), and split over the respective Python functions
- All jobs are now run using [start_job.sh](scripts/start_job.sh), using one function from [preparation.py](caroline/preparation.py) and optionally one bash file generated from [templates](templates)
- The scheduler is now fully Python-implemented 
- The installation on Spider is now Python-based
- The CAROLINE virtual environment is automatically updated during installation
- area-track-lists and parameter files are now stored in [config](config)
- Plugins are now installed in a central `caroline-plugins` location from the central configuration
- All bash scripts and other modular scripts are centralized in [scripts](scripts)
- The portal upload is split off from `run-caroline.sh` and now checks ever hour
- Crontab example now includes all necessary bash files
- Parameters to be replaced in templates are now indicated by `**parameter**` instead of `{parameter}`

### Fixed:
- Debug folders are now ignored
- [README.md](README.md) reflects the current state of the repository 
- Contents of `caroline` folder are now ruff-compliant
- KML generation code is now more understandable
- Template for `DeInSAR.py` is now human-readable
- Template for `re-SLC.py` is now human-readable

### Deprecated:
- Airflow management
- Download management using Airflow
- Interferogram processing using Airflow

### Removed:
- Prototype directory
- CAROLINE manager scripts
- CAROLINE version from parameter file names and variables
- Deprecated setup configuration from [setup.py](setup.py)


## [v1.0.0](https://github.com/TUDelftGeodesy/caroline/tree/c141134e837314b9d38aa5778add312d6b0b0a4d) (01-Apr-2025, [diff](https://github.com/TUDelftGeodesy/caroline/compare/4b8492b1dfa424735f65cf38b717c89501c76996...c141134e837314b9d38aa5778add312d6b0b0a4d))

### Added:
- Ruff workflow on pull request
- Ruff workflow on pre-commit hook
- AoI dependencies
- AoIs `id_jakarta_large`, `id_jakarta`, `id_jakarta_cubic`, `gr_santorini`, `nl_woerden`, `nl_amsterdam`, `nl_amsterdam_extended`, `nl_amsterdam_tsx`, `nl_assendelft`, `nl_grijpskerk`, `nl_groningen`, `nl_groningen_depsi`, `nl_limburg`, `nl_limburg_stack`, `nl_nieuwolda`, `nl_north_holland_south_tsx`, `nl_schoonebeek`, `nl_veenweiden`, `nl_zegveld`, `sg_singapore`
- Daily generating AoI extent overview kml containing AoIs, coregistered stacks, and downloaded SLCs
- Daily log email
- Ability to force-start AoIs
- Ability to upload portal layers to different Skygeo customers (instead of only `caroline`)
- Warning emails to the admins if portal layer upload fails due to `ssh` keys missing
- Send emails upon completion of a job
- Logging of all jobs to a central log
- Bash file `summarize-running-jobs.sh` to get information on all running jobs
- Job `crop` as a more stable replacement for `Stack stitching`
- Job `DeInSAR` for non-Sentinel-1 coregistration
- Support for other sensors in `crop`, `DePSI`
- Reference point modes `independent`, `constant`, and `hardcoded` in `DePSI`
- Job `Re-SLC` to generate zarr-stacks
- Single-polarisation images are now supported in the incomplete download filter
- Detection of which jobs completed correctly and which did not
- Test script running on `short` partition to allow testing before pushing live
- Project owner, engineer, objective and notes

### Changed:
- Upload portal layers from the login node instead of from the compute node due to firewall issues
- Send emails using `sendmail` instead of `mailx`
- Reflect changed OS in recompiled C code for Gdal environment
- Add upload date to portal layers to avoid name clashes
- Sort the Python files into `OLD`, `generate`, `setup`, and `wait`
- Parameter files are now read into a dictionary instead of a list
- DEMs are now managed from the parameter file to allow non-Netherlands AoIs

### Fixed:
- CAROLINE is installable from `pyproject.toml`
- Align DEM of the Netherlands properly
- Multi-track starts will no longer crash in `DePSI` generation if earlier steps crashed
- Downloads are now detected using `json` files instead of the no longer provided `xml` files
- Installs are blocked when `re-SLC` or `crop` is running to avoid those jobs crashing
- Add plugin patches to `ps_calibration.m` and `get_stack_parameters.m` (`DePSI`), and `ps_post_write_shape_csv.m` (`DePSI_post`)
- Code is no longer run in the Software directory but rather in a separate `run` directory

### Removed:
- `Stack stitching` job (replaced by `crop`)

## [v0.2.0](https://github.com/TUDelftGeodesy/caroline/tree/4b8492b1dfa424735f65cf38b717c89501c76996) (14-Apr-2023, [diff](https://github.com/TUDelftGeodesy/caroline/compare/afd68b0489cee6f70e73485a1b815d6a8bb5e932...4b8492b1dfa424735f65cf38b717c89501c76996))

### Added:
- Wrapper to run from cron
- Detection when new image is downloaded
- Area-track-lists to trigger AoIs when new images are downloaded
- Upload possibility to SkyGeo viewers under `caroline` user
- `README` for `Stack stitching`
- Custom shapefile support
- Support for `CAROLINE` environment variable
- Track support in `CAROLINE.sh`
- Config file support in `CAROLINE.sh`
- Installation script on `Spider`
- Possibility to add patches to plugins
- Patch to `ps_read_process_directory` in `DePSI`
- AoI `nl_amsterdam` 

### Changed
- CAROLINE now supports `SLURM`-managed HPCs instead of `Queue Submission`-managed HPCs
- `Stack stitching` output is now stored in `cropped_stack` instead of `<AoI_name>_cropped_stack`
- `Stack stitching` output files no longer have the `AoI_name` in the name
- `cpxfiddle` is treated as a plugin instead of an always available command
- `DePSI`, `RDNAPtrans`, `Geocoding` and `DePSI_post` now have mutable paths
- `DePSI_post` plugin is updated to 2.1.4.0
- `DePSI_post` parameters are added to the parameter file
- `Matlab` supported version is changed from `R2020a` to `R2021b`
- `Stack stitching` now runs on 2 cpus instead of 1
- DEMs are now specified from the parameter file
- Previous `DePSI` results are moved to a date-annotated folder instead of overwritten

### Fixed
- `Tarball` mode in `DePSI_post` will no longer also create `csv` output
- `Stack stitching` scripts are cleaned from excess code
- Always include the `mother` image in the `Doris v5` stack generation
- Proper detection of `h2ph` files in `Stack stitching`
- `job_id` files for `DePSI-post` and `mrm` are now stored in the `psi` directory instead of the base `DePSI` directory
- Incomplete downloads are removed properly in a second run

### Removed
- Excess files in `Stack stitching`
- Broken soft links

## [v0.1.0](https://github.com/TUDelftGeodesy/caroline/tree/afd68b0489cee6f70e73485a1b815d6a8bb5e932) (16-Aug-2022)

### Added:

- `Doris v5` job
- `Stack stitching` job
- `DePSI` v2.2.1.1 job
- `DePSI_post` v2.1.2.0 job
- Tarball job
- Support for running on a `Queue Submission`-managed HPC
- Rectangular AoI support
- CAROLINE manager script
- Initial download support via DAG
- Initial Airflow workflows via DAG
- Interferogram generation via DAG