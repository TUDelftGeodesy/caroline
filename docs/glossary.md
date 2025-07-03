# CAROLINE Glossary

This file details the definitions of terms used in the [CAROLINE architecture](#caroline-architecture), [High-Performance Cluster usage](#hpc-functionality), and [the details of what each job does](#jobs).  

## CAROLINE Architecture
- <b>module</b>: a block in the CAROLINE [architecture](architecture.md). An example is the <i>autonomous stack building</i> module. A module has one or more submodules.
- <b>submodule</b>: a component of a module. An example is <i>coregistration</i>, part of the <i>autonomous stack building</i> module. A submodule has one or more jobs.
- <b>job</b>: a single program that achieves a clearly specified goal, that is individually submitted to the SLURM manager. The <i>coregistration</i> submodule contains three jobs: <i>Doris v5</i> (Sentinel-1 coregistration), <i>Doris v5 cleanup</i>, and <i>DeInSAR</i> (for coregistration of other sensors). A job consists of exactly one function call to a preparation function, and optionally one bash script to be executed.
- <b>function</b>: a Python function.
- <b>plugin</b>: an external software package that is called by CAROLINE to execute a job. An example is the <i>Doris v5.0.4</i> plugin, used in the job <i>Doris v5</i> in the coregistration submodule.
- <b>patch</b>: an amendment to a plugin, where the original plugin code does not function as intended for CAROLINE. All patches are located in the `patches` directory, using the exact same folder structure as will be generated in the directory read from the `CAROLINE_PLUGINS_DIRECTORY` setting.
- <b>workflow</b>: the string of consecutive jobs required to reach a specific outcome. E.g., for a psi_batch portal layer starting from a coregistered stack, the workflow is `crop_to_raw` > `DePSI` > `mrm` > `DePSI_post` > `portal upload`

- <b>status file</b>: a file detailing the status, progress, and errors of a job, produced by the job itself (so not the command line output). 

## HPC Functionality
- <b>Compute node</b>: a processor specifically intended for larger computations, on which all CAROLINE jobs are run
- <b>cronjob</b>: a job being started at specified intervals. Cronjobs will always run on login nodes
- <b>crontab</b>: the file specifying the cronjobs
- <b>HPC</b>: High-Performance Cluster, colloquially known as a supercomputer
- <b>Login node</b>: a processor on which users can interact with the file systems of an HPC, and on which cronjobs will run
- <b>SLURM manager</b>: the compute load manager that assigns jobs to compute nodes
- <b>squeue</b>: the list of jobs that have been submitted to the SLURM manager, and are currently running or waiting to run

- <b>job ID</b>: the number a job is assigned when it is submitted to the squeue. The output of the job will be in `slurm-<job ID>.out`

## Jobs
All jobs run on a single AoI on a single track. The following specifications will assume this.

- <b>s1_download</b>: this job checks if all original SLCs acquired between the specified start date and end date that are available on ASF have been downloaded to the HPC. This is achieved by querying the ASF servers and downloading any missing original SLCs.
    * input:
      * AoI in `.shp` format
    * output:
      * Original SLCs
- <b>doris</b>: this job performs the basic interferometric Sentinel-1 procedure per image pair. This includes orbit corrections, coregistration, resampling, burst merging, interferogram generation, reference phase and DEM (including reference ellipsoid) subtraction, geocoding, and coherence estimation.
    * input:
      * Original SLCs
      * AoI in `.shp` format
      * Digital Elevation Model covering the entirety of the original SLCs in `.raw` format
    * output:
      * Selection of bursts intersecting with the provided AoI (+ a small buffer)
      * Burstwise complex interferograms with reference DEM subtracted (`cint_srd.raw`)
      * Burstwise height-to-phase screens with the reference DEM subtracted (`h2ph_srd.raw`)
      * Burstwise logs of operations performed (`master.res` for the mother, `slave.res` for the daughters)
      * Burstwise geocoded pixel coordinates (`lam.raw` and `phi.raw`)
      * Burstwise resampled reramped SLC of the mother image with the reference DEM subtracted (`slave_rsmp_reramped.raw`)
      * Burstwise radarcoded DEM (`dem_radar.raw`)
      * All above products, but merged into one rectangular file instead of per burst
- <b>doris_cleanup</b>: this job removes excess files produced by `doris_v5`
    * input:
      * A directory in which `doris_v5` has run
    * output:
      * The removal of intermediate files not necessary for any subsequent step
- <b>deinsar</b>: this job performs the basic interferometric  procedure per image pair for the sensors `"ERS", "ENV", "TSX", "TDX", "PAZ", "RSAT2", "Cosmo"`, and `"ALOS2"`. This includes cropping, orbit corrections, coregistration, resampling, interferogram generation, reference phase and DEM (including reference ellipsoid) subtraction, coherence estimation, and geocoding.
    * input:
      * Original SLCs
      * AoI in `.shp` format
      * Digital Elevation Model covering the entirety of the original SLCs in `.raw` format
    * output:
      * Complex interferograms with reference DEM subtracted cropped to the AoI (`cint_srd.raw`)
      * Height-to-phase screens with the reference DEM subtracted cropped to the AoI (`h2ph_srd.raw`)
      * Logs of operations performed (`slave.res`)
      * Geocoded pixel coordinates cropped to the AoI (`lam.raw` and `phi.raw`)
      * Resampled SLC of the mother image with the reference DEM subtracted cropped to the AoI (`slave_rsmp.raw`)
      * Radarcoded DEM (`dem_radar.raw`)
- <b>crop_to_raw</b>: this job crops the output complex interferograms, height-to-phase screens, geocoded coordinates and mother SLC of `deinsar` or `doris` to a provided AoI. The crop is taken to be the smallest rectangle in line/pixel coordinates that completely encloses the AoI. It then creates the (now resampled and reference DEM-subtracted, i.e.,  _reduced_) SLCs from the cropped complex interferograms and the mother SLC.
  * input:
    * Complex interferograms with reference DEM subtracted (`cint_srd.raw`)
    * Height-to-phase screens with the reference DEM subtracted (`h2ph_srd.raw`)
    * Logs of operations performed (`master.res`/`slave.res`)
    * Geocoded pixel coordinates (`lam.raw` and `phi.raw`)
    * Resampled (S-1 reramped) SLC of the mother image with the reference DEM subtracted (`slave_rsmp.raw` or `slave_rsmp_reramped.raw`)
    * Radarcoded DEM (`dem_radar.raw`)
    * AoI in `.shp` format
  * output:
    * Radarcoded DEM cropped to the AoI (`dem_radar.raw`)
    * Geocoded pixel coordinates cropped to the AoI (`lam.raw` and `phi.raw`)
    * Complex interferograms with reference DEM subtracted cropped to the AoI (`cint_srd.raw`)
    * Height-to-phase screens with reference DEM subtracted cropped to the AoI (`h2ph_srd.raw`)
    * Reduced SLCs with reference DEM subtracted cropped to the AoI (`slc_srd.raw`)
    * Line and pixel specification of the crop (`nlines_crop.txt` and `npixels_crop.txt`)
- <b>crop_to_zarr</b>: this job converts the output complex interferograms, height-to-phase screens, geocoded coordinates and mother SLC of `doris` or `deinsar` into a [sarxarray](https://github.com/TUDelftGeodesy/sarxarray) stack. It then crops all data to a provided AoI. The crop is taken to be the smallest rectangle in line/pixel coordinates that completely encloses the AoI. Finally, it creates the (now resampled and reference DEM-subtracted, i.e.,  _reduced_) SLCs from the cropped complex interferograms and the mother SLC.
  * input:
    * Complex interferograms with reference DEM subtracted (`cint_srd.raw`)
    * Height-to-phase screens with the reference DEM subtracted (`h2ph_srd.raw`)
    * Logs of operations performed (`master.res`/`slave.res`)
    * Geocoded pixel coordinates (`lam.raw` and `phi.raw`)
    * Resampled (S-1 reramped) SLC of the mother image with the reference DEM subtracted (`slave_rsmp.raw` or `slave_rsmp_reramped.raw`)
    * Radarcoded DEM (`dem_radar.raw`)
    * AoI in `.shp` format
  * output:
    * `.zarr` archive with the following fields:
      - variables:
        * `h2ph`: height-to-phase screen with the reference DEM subtracted cropped to the AoI
        * `imag`: imaginary component of the reduced SLCs cropped to the AoI
        * `real`: real component of the reduced SLCs cropped to the AoI
      - coordinates:
        * `azimuth`: azimuth coordinates cropped to the AoI (the original origin of the input is retained throughout the crop)
        * `range`: range coordinates cropped to the AoI (the original origin of the input is retained throughout the crop)
        * `lat`: latitude coordinates cropped to the AoI
        * `lon`: longitude coordinates cropped to the AoI
        * `time`: epochs of the acquisitions
- <b>stm_generation</b>: this job identifies PS in a `.zarr`-archive with a stack of coregistered, resampled, reduced SLCs.
  * input:
    * `.zarr` archive with the following fields:
      - variables:
        * `h2ph`: height-to-phase screen with the reference DEM subtracted cropped to the AoI
        * `imag`: imaginary component of the reduced SLCs cropped to the AoI
        * `real`: real component of the reduced SLCs cropped to the AoI
      - coordinates:
        * `azimuth`: azimuth coordinates cropped to the AoI (the original origin of the input is retained throughout the crop)
        * `range`: range coordinates cropped to the AoI (the original origin of the input is retained throughout the crop)
        * `lat`: latitude coordinates cropped to the AoI
        * `lon`: longitude coordinates cropped to the AoI
        * `time`: epochs of the acquisitions
  * output:
    * `.zarr` archive with the following fields:
      - variables:
        * `h2ph`...
      - coordinates:
- <b>depsi</b>: this job runs [Delft Persistent Scatterer Interferometry (DePSI)](https://repository.tudelft.nl/record/uuid:5dba48d7-ee26-4449-b674-caa8df93e71e) on the output of `crop_to_raw`.
    * input:
      * Radarcoded DEM cropped to the AoI (`dem_radar.raw`)
      * Geocoded pixel coordinates cropped to the AoI (`lam.raw` and `phi.raw`)
      * Complex interferograms with reference DEM subtracted cropped to the AoI (`cint_srd.raw`)
      * Height-to-phase screens with reference DEM subtracted cropped to the AoI (`h2ph_srd.raw`)
      * Reconstructed SLCs with reference DEM subtracted cropped to the AoI (`slc_srd.raw`)
      * Line and pixel specification of the crop (`nlines_crop.txt` and `npixels_crop.txt`)
    * output:
      * Estimated time series of identified persistent scatterers with respect to a reference point provided in `<AoI_name>_ref_sel1.raw`
      * Multi-image Reflectivity Map (MRM) of the AoI (`<AoI_name>_mrm.raw`)
- <b>mrm</b>: this job converts the MRM produced by `depsi` into `.ras` format for usage in `depsi_post`.
    * input:
      * Multi-image Reflectivity Map (MRM) of the AoI (`<AoI_name>_mrm.raw`) as produced by `depsi`
    * output:
      * Multi-image Reflectivity Map (MRM) of the AoI in `.ras` format
- <b>depsi_post</b>: this job extracts the time series from the `depsi` output into `.csv` format compatible with the web portal, as well as `.mat` files for importing into Matlab for post-processing.
    * input:
      * Estimated time series of identified persistent scatterers with respect to a reference point from `depsi`
      * Multi-image Reflectivity Map (MRM) of the AoI in `.ras` format
    * output:
      * `<AoI_name>_portal.csv` & `<AoI_name>_portal.json`, the two files that will be uploaded to the SkyGeo portal containing the estimated displacement time series per scatterer.
      * A Matlab archive containing the estimated displacement time series and amplitude time series per scatterer.
- <b>portal_upload</b>: this job creates a flag for [manage-portal-upload.sh](../scripts/manage-portal-upload.sh) to notify it that a portal layer is ready to be uploaded.
  * input:
    * A directory containing `depsi_post` output
  * output:
    * A `.txt` file in `PORTAL_UPLOAD_FLAG_DIRECTORY` containing a status (`TBD`, To Be Done), the directory containing the output, and the details of the viewer to which the layer should be uploaded.
- <b>tarball</b>: this job stores the output of `depsi_post` in a `.tar.gz` tarball archive for convenient downloading and further analysis on a local computer.
  * input:
     * A directory containing `depsi_post` output
  * output:
     * A `.tar.gz` tarball archive with the `depsi_post` output 
- <b>email</b>: this job sends an email containing the details of all processes that have run on this AoI and track. Whether or not a job is included in the email is controlled from [job-definitions.yaml](../config/job-definitions.yaml).
    * input:
      * `submission-log.csv`, containing the job IDs of all submitted jobs.
    * output:
      * An email detailing the details of the AoI, which processes were run successfully and which failed to complete, the links to the output files, and the contents of status files.
