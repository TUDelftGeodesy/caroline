# The CAROLINE parameter file

## General parameters
- `active`
  - Function: indicate whether an AoI should be processed. `1` will include the AoI in the live Caroline run, `0` will exclude it.
  - Possible values: `0`, `1`
- `project_owner`
  - Function: indicate the owner (i.e., the one responsible for this AoI)
  - Possible values: any `string`
- `project_owner_email`
  - Function: indicate the email of `project_owner`
  - Possible values: any `string`
- `project_engineer`
  - Function: indicate the engineer (i.e., the one responsible for the settings for this AoI)
  - Possible values: any `string`
- `project_engineer_email`
  - Function: indicate the email of `project_engineer`
  - Possible values: any `string`
- `project_objective`
  - Function: indicate the objective that is achieved by processing this AoI
  - Possible values: any `string`
- `project_notes`
  - Function: indicate any noteworthy settings that are not immediately obvious from `project_objective` but are relevant for interpretation.
  - Possible values: any `string`
- `three_letter_id`
  - Function: provide an identification means in the [squeue](glossary.md#hpc-functionality) for this AoI when it is processing
  - Possible values: any `string` of exactly three uppercase alphanumeric characters
- `sensor`
  - Function: specify the satellite sensor that should be used
  - Possible values: `'S1'`, `'TSX'`, `'ERS'`, `'ENV'`, `'TDX'`, `'PAZ'`, `'RSAT2'`, `'Cosmo'`, `'ALOS2'`
- `polarisation`
  - Function: specify the polarisations that should be processed
  - Possible values: `list` containing a set of the values `'VVVH'` (only Sentinel-1), `'HH'`, `'HV'`, `'VH'`, `'VV'` (non-Sentinel-1). Example `['VVVH']` or `['HH', 'VV']`.
- `product_type`
  - Function: specify the product that should be downloaded in case the job `s1_download` is requested. 
  - Possible values: Default is `"SLC"` since this is what further steps work with, other options can be passed as string. All options are documented by ASF [here](https://github.com/asfadmin/Discovery-asf_search/blob/master/asf_search/constants/PRODUCT_TYPE.py).
- `dependency`
  - Function: allow cross-AoI dependencies (e.g., one coregistration for multiple AoIs)
  - Possible values: `'None'`, or any other AoI where the parameter file `param_file_<AoI>.txt` exists in [config/parameter-files](../config/parameter-files), formatted as `'<AoI>'`
- `do_s1_download`
  - Function: switch to enable the [job](glossary.md#jobs) `s1_download` in the Download submodule
  - Possible values: `0`, `1`
- `do_coregistration`
  - Function: switch to enable the [jobs](glossary.md#jobs) `doris` and `doris_cleanup`, or `deinsar`, in the Coregistration submodule
  - Possible values: `0`, `1`
- `do_crop_to_raw`
  - Function: switch to enable the [job](glossary.md#jobs) `crop_to_raw` in the Cropping submodule
  - Possible values: `0`, `1`
- `do_crop_to_zarr`
  - Function: switch to enable the [job](glossary.md#jobs) `crop_to_zarr` in the Cropping submodule
  - Possible values: `0`, `1`
- `do_depsi`
  - Function: switch to enable the [job](glossary.md#jobs) `depsi` in the PSI-batch submodule
  - Possible values: `0`, `1`
- `do_depsi_post`
  - Function: switch to enable the [jobs](glossary.md#jobs) `mrm`, `depsi_post`, and (`portal_upload` or `tarball`) in the PSI-batch submodule
  - Possible values: `0`, `1`
- `depsi_post_mode`
  - Function: switch to select either the [job](glossary.md#jobs) `portal_upload` or `tarball` after running `depsi_post`
  - Possible values: `'csv'` (for `portal_upload`), `'tarball'` (for `tarball`)
- `skygeo_customer`:
  - Function: select the `customer` in the URL of the SkyGeo portal. The portal link is https://caroline.portal-tud.skygeo.com/portal/<skygeo_customer>/<skygeo_viewer>/viewers/basic/ . Switching away from the default `caroline` allows sharing specific datasets with customers.
  - Possible values: any `string` containing only alphanumeric lowercase characters, default `'caroline'`
- `skygeo_viewer`:
  - Function: select the `viewer` in the URL of the SkyGeo portal. The portal link is https://caroline.portal-tud.skygeo.com/portal/<skygeo_customer>/<skygeo_viewer>/viewers/basic/ .
  - Possible values: any `string` containing only alphanumeric lowercase characters
- `coregistration_AoI_name`
  - Function: specify the AoI name for the directory naming in the [jobs](glossary.md#jobs) `doris` and `doris_cleanup`, or `deinsar` in the Coregistration submodule. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `coregistration_directory`
  - Function: specify the base directory where the [jobs](glossary.md#jobs) `doris` and `doris_cleanup`, or `deinsar`, should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/stacks'`
- `crop_to_raw_AoI_name`
  - Function: specify the AoI name for the directory naming in the [job](glossary.md#jobs) `crop_to_raw` in the Cropping submodule. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `crop_to_raw_directory`
  - Function: specify the base directory where the [job](glossary.md#jobs) `crop_to_raw` should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/crops'`
- `crop_to_zarr_AoI_name`
  - Function: specify the AoI name for the directory naming in the [job](glossary.md#jobs) `crop_to_zarr` in the Cropping submodule. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `crop_to_zarr_directory`
  - Function: specify the base directory where the [job](glossary.md#jobs) `crop_to_zarr` should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/stacks_zarr'`
- `depsi_AoI_name`
  - Function: specify the AoI name for the directory naming in the [jobs](glossary.md#jobs) `depsi`, `mrm`, `depsi_post`, and `tarball` in the PSI-batch submodule. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `depsi_directory`
  - Function: specify the base directory where the [jobs](glossary.md#jobs) `depsi`, `mrm`, `depsi_post`, and `tarball` should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/projects/<AoI_name>/depsi'`
- `shape_AoI_name`
  - Function: specify the AoI name for the shapefile, typically the same as the AoI name. The shapefile will be saved as `<shapefile_name>_shape.shp`
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `shape_directory`
  - Function: specify the base directory where the shapefile should be stored. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Software/roi/<first step that will be run out of stacks / crops / depsi>/<country_code>_<region_of_interest>'`, where `stacks` indicates `coregistration` and `crops` indicates `crop_to_raw`.
- `shape_file`
  - Function: provide a link to a predetermined shapefile
  - Possible values: `''` for rectangular AoI generation, or `string` with any valid path to a shapefile on Spider, including the name of the shapefile itself ending in `.shp`. It is assumed the corresponding `.dbf`, `.prj` and `.shx` also exist with the same name (except the format) in the same directory.
- `center_AoI`
  - Function: provide the center coordinate in latitude/longitude for rectangular shapefile generation. Ignored if a shapefile is provided in `shape_file`.
  - Possible values: `list` of two numbers, the first the latitude, the second the longitude. E.g. `[52.371436, 4.897088]` for central Amsterdam.
- `AoI_width`
  - Function: specify the east-west AoI size in kilometers for rectangular shapefile generation. Ignored if a shapefile is provided in `shape_file`.
  - Possible values: any positive number, below `50` is recommended for processing time reasons.
- `AoI_length`
  - Function: specify the north-south AoI size in kilometers for rectangular shapefile generation. Ignored if a shapefile is provided in `shape_file`.
  - Possible values: any positive number, below `50` is recommended for processing time reasons.
- `track`:
  - Function: this parameter exists for the [scheduler](../caroline/scheduler.py). Any value will be overwritten, so keep it empty.
  - Possible values: `[]` (anything else is overwritten)
- `asc_dsc`
  - Function: this parameter exists for the [scheduler](../caroline/scheduler.py). Any value will be overwritten, so keep it empty.
  - Possible values: `[]` (anything else is overwritten)
- `include_tracks`
  - Function: Add any tracks not automatically detected by querying the ASF servers for Sentinel-1 track overlap in the last month. For non-Sentinel-1, add all tracks here.
  - Possible values: `[]`, or list of tracks formatted as `[s1_dsc_t037]`
- `exclude_tracks`
  - Function: Remove any tracks automatically detected by querying the ASF servers for Sentinel-1 track overlap in the last month, but one is not interested in.
  - Possible values: `[]`, or list of tracks formatted as `[s1_dsc_t037]`
- `start_date`
  - Function: specify the beginning of the processing interval. This date does not have to be present in the imaging stack, but will be included if it is present.
  - Possible values: `'YYYY-MM-DD'`
- `end_date`
  - Function: specify the end of the processing interval. This date does not have to be present in the imaging stack, but will be included if it is present. 
  - Possible values: `'YYYY-MM-DD'`, set to `9999-12-31` for live processing.
- `master_date`
  - Function: specify the mother (previously master) of the coregistered image stack. This date does not have to be present in the imaging stack, Caroline will use the first image on or after this date as mother.
  - Possible values: `'YYYY-MM-DD'`
- `send_completion_email`
  - Function: specify the email addresses of everyone that should be notified of a finished run of this AoI
  - Possible values: `'<email_1>(,<email_2>)*'`, comma-separated emails without spaces. Set to `''` for no email.
- `coregistration_partition`
  - Function: specify the partition on which the [jobs](glossary.md#jobs) `doris` or `deinsar` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `crop_to_raw_partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `crop_to_raw` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `crop_to_zarr_partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `crop_to_zarr` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `depsi_partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `depsi` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `depsi_post_partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `depsi_post` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)


## DEM parameters

## Doris parameters

## DeInSAR parameters

## Crop_to_zarr parameters

## DePSI parameters

## DePSI_post parameters