# The CAROLINE parameter file

In the following section, the symbol `:` is used as a separator for YAML layers. For example, the key `general:project:owner:name` in the YAML looks like
```yaml
general:
  project:
    owner:
      name: "value"
```

Required fields for any AoI are marked with a bold **R**
## General parameters
- `general:active`
  - Function: indicate whether an AoI should be processed. `1` will include the AoI in the live Caroline run, `0` will exclude it.
  - Possible values: `0`, `1`
- **R** `general:project:owner:name`
  - Function: indicate the owner (i.e., the one responsible for this AoI)
  - Possible values: any `string`
- **R** `general:project:owner:email`
  - Function: indicate the email of the project owner
  - Possible values: any `string`
- **R** `general:project:engineer:name`
  - Function: indicate the engineer (i.e., the one responsible for the settings for this AoI)
  - Possible values: any `string`
- **R** `general:project:engineer:email`
  - Function: indicate the email of the project engineer
  - Possible values: any `string`
- **R** `general:project:objective`
  - Function: indicate the objective that is achieved by processing this AoI
  - Possible values: any `string`
- **R** `general:project:notes`
  - Function: indicate any noteworthy settings that are not immediately obvious from `project_objective` but are relevant for interpretation.
  - Possible values: any `string`
- **R** `general:project:three-letter-id`
  - Function: provide an identification means in the [squeue](glossary.md#hpc-functionality) for this AoI when it is processing
  - Possible values: any `string` of exactly three uppercase alphanumeric characters
- `general:input-data:sensor`
  - Function: specify the satellite sensor that should be used, default `'S1'`
  - Possible values: `'S1'`, `'TSX'`, `'ERS'`, `'ENV'`, `'TDX'`, `'PAZ'`, `'RSAT2'`, `'Cosmo'`, `'ALOS2'`
- `general:input-data:polarisation`
  - Function: specify the polarisations that should be processed
  - Possible values: `list` containing a set of the values `'VVVH'` (only Sentinel-1), `'HH'`, `'HV'`, `'VH'`, `'VV'` (non-Sentinel-1). Example `['VVVH']` or `['HH', 'VV']`.
- `general:input-data:product-type`
  - Function: specify the product that should be downloaded in case the job `s1_download` is requested. 
  - Possible values: Default is `"SLC"` since this is what further steps work with, other options can be passed as string. All options are documented by ASF [here](https://github.com/asfadmin/Discovery-asf_search/blob/master/asf_search/constants/PRODUCT_TYPE.py).
- **R** `general:workflow:dependency:aoi-name`
  - Function: allow cross-AoI dependencies (e.g., one coregistration for multiple AoIs)
  - Possible values: empty, or any other AoI where the parameter file `param-file-<AoI>.yaml` exists in [the parameter file repository](https://github.com/TUDelftGeodesy/caroline-parameter-files/tree/main/parameter-files), formatted as `'<AoI>'`, optionally with the `-` character replaced by `_`
- **R** `general:workflow:dependency:input-step`
  - Function: allow cross-AoI dependencies (e.g., one coregistration for multiple AoIs). This is the step that will be used as input, not necessarily the last step in that AoI
  - Possible values: any [job name](glossary.md#jobs)
- **R** `general:workflow:output-steps`
  - Function: specify the desired output jobs
  - Possible values: list of any [job names](glossary.md#jobs)
- `general:workflow:filters:depsi_post-output`
  - Function: switch to select either the [job](glossary.md#jobs) `portal_upload` or `tarball` after running `depsi_post`
  - Possible values: `'csv'` (for `portal_upload`), `'tarball'` (for `tarball`)
- `general:portal:skygeo-customer`:
  - Function: select the `customer` in the URL of the SkyGeo portal. The portal link is https://caroline.portal-tud.skygeo.com/portal/<skygeo_customer>/<skygeo_viewer>/viewers/basic/ . Switching away from the default `caroline` allows sharing specific datasets with customers.
  - Possible values: any `string` containing only alphanumeric lowercase characters, default `'caroline'`
- `general:portal:skygeo-viewer`:
  - Function: select the `viewer` in the URL of the SkyGeo portal. The portal link is https://caroline.portal-tud.skygeo.com/portal/<skygeo_customer>/<skygeo_viewer>/viewers/basic/ .
  - Possible values: any `string` containing only alphanumeric lowercase characters
- `general:shape-file:aoi-name` (machine field)
  - Function: specify the AoI name for the shapefile, typically the same as the AoI name. The shapefile will be saved as `<shapefile_name>_shape.shp`
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `general:shape-file:directory` (machine field)
  - Function: specify the base directory where the shapefile should be stored. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Software/roi/<first step that will be run out of stacks / crops / depsi>/<country_code>_<region_of_interest>'`, where `stacks` indicates `coregistration` and `crops` indicates `crop_to_raw`.
- **R** `general:shape-file:shape-file-link`
  - Function: provide a link to a predetermined shapefile. If this field is provided, the `rectangular-shape-file` keys are ignored
  - Possible values: `''` for rectangular AoI generation, or `string` with any valid path to a shapefile on Spider, including the name of the shapefile itself ending in `.shp`. It is assumed the corresponding `.dbf`, `.prj` and `.shx` also exist with the same name (except the format) in the same directory.
- **R** `general:shape-file:rectangular-shape-file:center-AoI`
  - Function: provide the center coordinate in latitude/longitude for rectangular shapefile generation. Ignored and not required if a shapefile is provided in `general:shape-file:shape-file-link`.
  - Possible values: `list` of two numbers, the first the latitude, the second the longitude. E.g. `[52.371436, 4.897088]` for central Amsterdam.
- **R** `general:shape-file:rectangular-shape-file:AoI-width`
  - Function: specify the east-west AoI size in kilometers for rectangular shapefile generation. Ignored and not required if a shapefile is provided in `general:shape-file:shape-file-link`.
  - Possible values: any positive number, below `50` is recommended for processing time reasons.
- **R** `eneral:shape-file:rectangular-shape-file:AoI-length`
  - Function: specify the north-south AoI size in kilometers for rectangular shapefile generation. Ignored and not required if a shapefile is provided in `general:shape-file:shape-file-link`.
  - Possible values: any positive number, below `50` is recommended for processing time reasons.
- `general:tracks:track` (machine field)
  - Function: this parameter exists for the [scheduler](../caroline/scheduler.py). Any value will be overwritten, so keep it empty.
  - Possible values: `[]` (anything else is overwritten)
- `general:tracks:asc_dsc` (machine field)
  - Function: this parameter exists for the [scheduler](../caroline/scheduler.py). Any value will be overwritten, so keep it empty.
  - Possible values: `[]` (anything else is overwritten)
- `general:tracks:include-tracks`
  - Function: Add any tracks not automatically detected by querying the ASF servers for Sentinel-1 track overlap in the last month. For non-Sentinel-1, add all tracks here.
  - Possible values: `[]`, or list of tracks formatted as `['s1_dsc_t037']`
- `general:tracks:exclude-tracks`
  - Function: Remove any tracks automatically detected by querying the ASF servers for Sentinel-1 track overlap in the last month, but one is not interested in.
  - Possible values: `[]`, or list of tracks formatted as `['s1_dsc_t037']`
- `general:timeframe:start`
  - Function: specify the beginning of the processing interval. This date does not have to be present in the imaging stack, but will be included if it is present.
  - Possible values: `'YYYY-MM-DD'`
- `general:timeframe:end`
  - Function: specify the end of the processing interval. This date does not have to be present in the imaging stack, but will be included if it is present. 
  - Possible values: `'YYYY-MM-DD'`, set to `'9999-12-31'` for live processing.
- `general:timeframe:mother`
  - Function: specify the mother (previously master) of the coregistered image stack. This date does not have to be present in the imaging stack, Caroline will use the first image on or after this date as mother.
  - Possible values: `'YYYY-MM-DD'`
- **R** `general:email:recipients`
  - Function: specify the email addresses of everyone that should be notified of a finished run of this AoI
  - Possible values: `'<email_1>(,<email_2>)*'`, comma-separated emails without spaces. Set to `''` for no email.
- `general:dem:file`
  - Function: specify the absolute path to the DEM file in `.raw` format. This DEM should cover the entire coregistration area (note: this is burstwise for Sentinel-1, so a lot larger than your AoI). Defaults to the Netherlands DEM
  - Possible values: `string` with absolute path to the DEM file, including the DEM filename in `.raw` format
- `general:dem:format`
  - Function: specify the format in which the DEM file is saved.
  - Possible values: `string` with the format, generally `'r4'` (real-4)
- `general:dem:size`
  - Function: specify the number of rows and columns in the DEM
  - Possible values: `list` with two integers: as first element the number of columns (north-south), as second element the number of rows (east-west)
- `general:dem:delta`
  - Function: specify the pixel size of the DEM in degrees
  - Possible values: `list` of two floats: `[delta_latitude, delta_longitude]`
- `general:dem:upperleft`
  - Function: specify the latitude and longitude of the upperleft corner of the DEM.
  - Possible values: `list` of two floats: `[latitude, longitude]`
- `general:dem:nodata`
  - Function: specify the filler value that should be interpreted as 'No data'
  - Possible values: Any number, generally -32768
- `general:steps:*` (machine field)
  - Function: specify which jobs should run, linked to the step keys in [job-definitions.yaml](../config/job-definitions.yaml)


## Crop_to_raw parameters

These parameters are used in the job `crop_to_raw`. Defaults in [the default crop_to_raw config file](../config/parameter-files/default-job-param-file-crop_to_raw.yaml).


- `crop_to_raw:general:AoI-name`: 
  - Function: specify the AoI name for the directory naming in the [job](glossary.md#jobs) `crop_to_raw`. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `crop_to_raw:general:directory`
  - Function: specify the base directory where the [job](glossary.md#jobs) `crop_to_raw` should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/stacks'`
- `crop_to_raw:general:partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `crop_to_raw` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
  
## Crop_to_zarr parameters

These parameters are used in the job `crop_to_zarr`. Defaults in [the default crop_to_zarr config file](../config/parameter-files/default-job-param-file-crop_to_zarr.yaml).


- `crop_to_zarr:general:AoI-name`: 
  - Function: specify the AoI name for the directory naming in the [job](glossary.md#jobs) `crop_to_zarr`. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `crop_to_zarr:general:directory`
  - Function: specify the base directory where the [job](glossary.md#jobs) `crop_to_zarr` should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/stacks'`
- `crop_to_zarr:general:partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `crop_to_zarr` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `crop_to_zarr:general:crop_to_zarr-code-directory`
  - Function: specify where the DePSI_group code is, containing the functionality for `crop_to_zarr`
  - Possible values: `string` with the absolute path to the base directory of `DePSI_group`

## DeInSAR parameters

These parameters are used in the job `deinsar`. Defaults in [the default DeInSAR config file](../config/parameter-files/default-job-param-file-deinsar.yaml).


- `deinsar:general:AoI-name`: 
  - Function: specify the AoI name for the directory naming in the [job](glossary.md#jobs) `deinsar`. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `deinsar:general:directory`
  - Function: specify the base directory where the [job](glossary.md#jobs) `deinsar` should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/stacks'`
- `deinsar:general:partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `deinsar` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `deinsar:general:deinsar-code-directory`
  - Function: specify the absolute path to the DeINSAR code
  - Possible values: `string` with the absolute path to the base directory of `DeInSAR`
- `deinsar:general:doris-v4-code-directory`
  - Function: specify the absolute path to the Doris v4 code
  - Possible values: `string` with the absolute path to the base directory of `doris_v4`
- `deinsar:input:data-directories`
  - Function: specify the data directories where the original images are stored (as the non-Sentinel-1 data archive is not sorted in a machine-readable way)
  - Possible values: e.g. `{'tsx_asc_t116': '/project/caroline/Data/radar_data/eurasia/netherlands/tsx/nl_amsterdam_tsx_asc_t116_T171816_171824_007_hh/data_backup'}`, as keys the tracks, as arguments the full path to the data directory, each key on a new line one tab in.
- `deinsar:deinsar-settings:do-orbit`
  - Function: specify whether the step `orbit` should be run (note: only for ENV, ERS and RSAT2)
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-crop`
  - Function: specify whether the step `crop` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-tsx-deramp`
  - Function: specify whether the step `tsx-deramp` should be run (note: only for TSX)
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-simamp`
  - Function: specify whether the step `simamp` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-mtiming`
  - Function: specify whether the step `mtiming` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-ovs`
  - Function: specify whether the step `ovs` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-choose-master`
  - Function: specify whether the step `choose-master` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-coarseorb`
  - Function: specify whether the step `coarseorb` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-coarsecorr`
  - Function: specify whether the step `coarsecorr` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:finecoreg:do-finecoreg`
  - Function: specify whether the step `finecoreg` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:finecoreg:finecoreg-mode`
  - Function: specify which version of `finecoreg` should be run
  - Possible values: `'simple'`, `'normal'`
- `deinsar:deinsar-settings:do-reltiming`
  - Function: specify whether the step `reltiming` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-dembased`
  - Function: specify whether the step `dembased` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-coregpm`
  - Function: specify whether the step `coregpm` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-resample`
  - Function: specify whether the step `resample` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-tsx-reramp`
  - Function: specify whether the step `tsx-reramp` should be run (note: only for TSX)
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-comprefpha`
  - Function: specify whether the step `comprefpha` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-comprefdem`
  - Function: specify whether the step `comprefdem` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-interferogram`
  - Function: specify whether the step `interferogram` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-subtrrefpha`
  - Function: specify whether the step `subtrrefpha` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-subtrrefdem`
  - Function: specify whether the step `subtrrefdem` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-coherence`
  - Function: specify whether the step `coherence` should be run
  - Possible values: `0`, `1`
- `deinsar:deinsar-settings:do-geocoding`
  - Function: specify whether the step `geocoding` should be run
  - Possible values: `0`, `1`


## DePSI parameters

These parameters are used in the job `depsi`. Defaults in [the default DePSI config file](../config/parameter-files/default-job-param-file-depsi.yaml)
Most parameters are explained in the [PhD thesis of Freek](https://repository.tudelft.nl/record/uuid:5dba48d7-ee26-4449-b674-caa8df93e71e) using the same naming (underscores and dashes may be swapped). Those that aren't:

- `depsi:general:AoI-name`: 
  - Function: specify the AoI name for the directory naming in the [jobs](glossary.md#jobs) `depsi`, `mrm`, and `depsi_post`. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `depsi:general:directory`
  - Function: specify the base directory where the [jobs](glossary.md#jobs) `depsi`, `mrm`, and `depsi_post` should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/stacks'`
- `depsi:general:partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `depsi` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `depsi:general:depsi-code-directory`
  - Function: specify where the DePSI code is
  - Possible values: `string` with the absolute path to the base directory of `depsi`
- `depsi:general:rdnaptrans-directory`
  - Function: specify where the [RDNAPtrans](https://www.nsgi.nl/coordinatenstelsels-en-transformaties/coordinatentransformaties/rdnap-etrs89-rdnaptrans) code is
  - Possible values: `string` with the absolute path to the base directory of RDNAPtrans
- `depsi:general:geocoding-directory`
  - Function: specify where the Geocoding code is
  - Possible values: `string` with the absolute path to the base directory of Geocoding
- `depsi:depsi-settings:general:ref-cn`
  - Function: specify the mode of how the reference point in DePSI should be determined
  - Possible values for the key `all`:
    - `[]` or `'independent'`: consecutive runs are treated as completely independent, and can therefore have different reference points. This can have unintended consequences as the behaviour of the reference point can change drastically. The reference point is determined using the NAD metric.
    - `'constant'`: consecutive runs on the same track use the same reference point, where the first run runs on mode `'independent'` to select a reference point, and further runs retain this point.
    - `[azimuth, range]`: all runs are forced to the specified reference point regardless of what is there. If the reference point is not in the selection, DePSI will throw an error
  - Additionally, one can add keys for individual tracks as new lines one tab in from `ref-cn`. This generates a dictionary that looks like this. `{'s1_asc_t088': 'constant', 's1_dsc_t110': [100, 300], 'all': 'constant'}`. Different behaviours are specified for different tracks. This is almost always necessary for the `[azimuth, range]` mode. If tracks are missing from this specification, the `'all'` key is used for those instead. All of the above options are allowed in this mode as arguments.
- `depsi:depsi-settings:psc:do-water-mask`
  - Function: specify whether a water mask should be applied. If it should be applied, a water mask named `water_mask_<depsi_AoI_name>_<sensor>_<asc_dsc>_t<track:0>3d>.raw` is expected in the water-mask directory in the [configuration file](../config/spider-config.yaml).
  - Possible values: `'yes'`, `'no'`

## DePSI_post parameters

These parameters are used in the job `depsi_post`. Defaults in [the default DePSI_post config file](../config/parameter-files/default-job-param-file-depsi_post.yaml)
Most parameters are explained in [How to DePSI-post](https://sites.google.com/site/radarcitg/resources/software/howto-depsi-post-proc?authuser=0) (underscores and dashes may be swapped). Note that some of these settings are preset for the Caroline processing flow and are thus not in the Caroline parameter file. Those that aren't in the Howto:

- `depsi:general:partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `depsi_post` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `depsi_post:general:depsi_post-code-directory`
  - Function: specify where the DePSI code is
  - Possible values: `string` with the absolute path to the base directory of `depsi_post`
- `depsi_post:general:cpxfiddle-directory`
  - Function: specify where the cpxfiddle executable is
  - Possible values: `string` with the absolute path to `cpxfiddle`


## Doris parameters
These parameters are used in the job `doris`. Defaults in [the default doris config file](../config/parameter-files/default-job-param-file-doris.yaml).

- `doris:general:AoI-name`: 
  - Function: specify the AoI name for the directory naming in the [jobs](glossary.md#jobs) `doris` and `doris_cleanup`. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `doris:general:directory`
  - Function: specify the base directory where the [jobs](glossary.md#jobs) `doris` and `doris_cleanup` should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/stacks'`
- `doris:general:partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `doris` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `doris:general:code-directory`
  - Function: specify the location of the Doris code.
  - Possible values: `string` with absolute path to the base of the Doris code
- `doris:doris-settings:do-coarse-orbits`
  - Function: specify whether the Doris step `coarse_orbits` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-deramp`
  - Function: specify whether the Doris step `deramp` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-reramp`
  - Function: specify whether the Doris step `reramp` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-fake-fine-coreg-bursts`
  - Function: specify whether the Doris step `fake_fine_coreg_bursts` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-fake-master-resample`
  - Function: specify whether the Doris step `fake_master_resample` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-dac-bursts`
  - Function: specify whether the Doris step `dac_bursts` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-fake-coreg-bursts`
  - Function: specify whether the Doris step `fake_coreg_bursts` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-resample`
  - Function: specify whether the Doris step `resample` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-reramp2`
  - Function: specify whether the Doris step `reramp` should be run (the second time it appears in the parameter file)
  - Possible values: `0`, `1`
- `doris:doris-settings:do-interferogram`
  - Function: specify whether the Doris step `interferogram` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-compref-phase`
  - Function: specify whether the Doris step `compref_phase` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-compref-dem`
  - Function: specify whether the Doris step `compref_dem` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-coherence`
  - Function: specify whether the Doris step `coherence` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-esd`
  - Function: specify whether the Doris step `esd` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-network-esd`
  - Function: specify whether the Doris step `network_esd` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-ESD-correct`
  - Function: specify whether the Doris step `ESD_correct` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-combine-master`
  - Function: specify whether the Doris step `combine_master` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-combine-slave`
  - Function: specify whether the Doris step `combine_slave` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-ref-phase`
  - Function: specify whether the Doris step `ref_phase` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-ref-dem`
  - Function: specify whether the Doris step `ref_dem` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-phasefilt`
  - Function: specify whether the Doris step `phasefilt` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-calc-coordinates`
  - Function: specify whether the Doris step `calc_coordinates` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-multilooking`
  - Function: specify whether the Doris step `multilooking` should be run
  - Possible values: `0`, `1`
- `doris:doris-settings:do-unwrap`
  - Function: specify whether the Doris step `unwrap` should be run
  - Possible values: `0`, `1`


## STM_generation parameters
These parameters are used in the job `stm_generation`. Defaults in [the default stm_generation config file](../config/parameter-files/default-job-param-file-stm_generation.yaml).


- `stm_generation:general:AoI-name`: 
  - Function: specify the AoI name for the directory naming in the [job](glossary.md#jobs) `stm_generation`. For cross-AoI dependencies, specify the same AoI name as the dependency.
  - Possible values: any `string` containing lowercase letters and underscores, typically matching the AoI name itself
- `stm_generation:general:directory`
  - Function: specify the base directory where the [job](glossary.md#jobs) `stm_generation` should run. 
  - Possible values: `string` with any valid path on Spider. If it does not exist, it will be created. Default is `'/project/caroline/Share/stacks'`
- `stm_generation:general:partition`
  - Function: specify the partition on which the [job](glossary.md#jobs) `stm_generation` should be run
  - Possible values: `'short'` (10h time limit, max 2 jobs), `'normal'` (5 day time limit), `'infinite'` (12 day time limit)
- `stm_generation:general:stm_generation-code-directory`
  - Function: specify where the DePSI_group code is, containing the functionality for `stm_generation`
  - Possible values: `string` with the absolute path to the base directory of `DePSI_group`

- `stm_generation:stm_generation-settings:ps-selection:mode`
  - Function: specify the mode to be used for the time frame selection during the PS selection
  - Possible values: `'full'` (full time series), `'initialization'` (using part of the time series defined by `stm_start_date_ps_selection` and `stm_initialization_length`)
- `stm_generation:stm_generation-settings:ps-selection:initialization-mode-settings:start-date`
  - Function: specify the start date of the time frame to be used for PS selection in `initialization` mode
  - Possible values: `'YYYY-MM-DD'`
- `stm_generation:stm_generation-settings:ps-selection:initialization-mode-settings:initialization-length`
  - Function: specify the length of the time frame to be used for PS selection in `initialization` mode
  - Possible values: any positive integer (# of epochs), or `'YYYY-MM-DD'` (end date)
- `stm_generation:stm_generation-settings:ps-selection:method`
  - Function: specify the method to be used for the PS selection
  - Possible values: `'nmad'`, `'nad'` 
- `stm_generation:stm_generation-settings:ps-selection:threshold`
  - Function: set the threshold for when a point is considered a PS (all PS below the threshold are accepted)
  - Possible values: any positive `float` 
- `stm_generation:stm_generation-settings:incremental-statistics:increment-mode`
  - Function: specify the mode to add either the [incremental or recalibration](https://github.com/TUDelftGeodesy/DePSI_group/blob/dev/depsi/point_quality.py#L148) NAD or NMAD (based on `stm_ps_selection_method`)
  - Possible values: `'incremental'` (update every epoch), `'recalibration'` (update every `stm_nad_nmad_recalibration_jump_size` epochs)
- `stm_generation:stm_generation-settings:incremental-statistics:recalibration-jump-size`
  - Function: specify the jump size to be used for `recalibration` mode for the updating NAD or NMAD
  - Possible values: any positive integer
- `stm_generation:stm_generation-settings:single-differences:mother`
  - Function: specify the mother epoch for single difference computations
  - Possible values: `'auto'` (uses the mother from the input `.zarr` archive), `'YYYY-MM-DD'`
- `stm_generation:stm_generation-settings:extra-projection`
  - Function: specify an extra projection to project the geolocation coordinates into
  - Possible values: `'RD'` (Dutch Rijksdriehoek, Netherlands only), `'EPSG:###'` (any code works), `''` (no new projection)
- `stm_generation:stm_generation-settings:partitioning:do-partitioning`
  - Function: switch to do or not do partitioning in time
  - Possible values: `0`, `1`
- `stm_generation:stm_generation-settings:partitioning:search-method`
  - Function: specify the method to search for the partitions
  - Possible values: `'pelt'`, `'binseg'`
- `stm_generation:stm_generation-settings:partitioning:cost-function`
  - Function: specify the cost function in the partition search
  - Possible values: `'l2'`
- `stm_generation:stm_generation-settings:partitioning:db-mode`
  - Function: specify whether or not to do the partition search on the Decibel scale
  - Possible values: `0` (advised), `1`
- `stm_generation:stm_generation-settings:partitioning:min-partition-length`
  - Function: specify the minimum number of acquisitions per partition
  - Possible values: any positive integer
- `stm_generation:stm_generation-settings:partitioning:undifferenced-output-layers`
  - Function: specify the output data layers per partition using the undifferenced input data
  - Possible values: `list` containing a subset of the following: `'nad'`, `'nmad'`, `mad`, `'quality_nmad_2sigma'`, `'quality_nmad_mean'`, `'quality_nad_2sigma'`, `'quality_nad_mean'`, `'amplitude_mean'`, `'amplitude_sigma'`, `'amplitude_median'`.
- `stm_generation:stm_generation-settings:partitioning:single-difference-output-layers`
  - Function: specify the output data layers per partition using the input data with a single difference in time with respect to `stm_single_difference_mother`
  - Possible values: `list` containing a subset of the following: `'nad'`, `'nmad'`, `mad`, `'quality_nmad_2sigma'`, `'quality_nmad_mean'`, `'quality_nad_2sigma'`, `'quality_nad_mean'`, `'amplitude_mean'`, `'amplitude_sigma'`, `'amplitude_median'`.
- `stm_generation:stm_generation-settings:outlier-detection:do-outlier-detection`
  - Function: switch to do or not do outlier detection in time
  - Possible values: `0`, `1`
- `stm_generation:stm_generation-settings:outlier-detection:window-size`
  - Function: specify the size of the rolling window across which the statistics are computed to determine whether or not an observation is an outlier
  - Possible values: any positive integer
- `stm_generation:stm_generation-settings:outlier-detection:db-mode`
  - Function: specify whether or not to do outlier detection on the Decibel scale
  - Possible values: `0`, `1` (advised)
- `stm_generation:stm_generation-settings:outlier-detection:n-sigma`
  - Function: specify the minimum number of sigma deviation from the median of the observations in the window before an observation is considered an outlier
  - Possible values: any positive `float` (advised 3)
