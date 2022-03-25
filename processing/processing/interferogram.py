
import datetime
import string
import sys
import shutil
import numpy as np
import os
import argparse
import pathlib
# packages installed to conda using pip are not picked my Pylace
from download import utils
from rippl.processing_templates.general_sentinel_1 import GeneralPipelines
from rippl.orbit_geometry.read_write_shapes import ReadWriteShapes


# Path to Doris RIPPL installation directory
# sys.path.extend(['/home/manuel/Documents/devel/satellite-livestreams/caroline/rippl'])
#
# from rippl.orbit_geometry.read_write_shapes import ReadWriteShapes
# from rippl.processing_templates.general_sentinel_1 import GeneralPipelines


if __name__ == '__main__':
    # First we read the input start and end date for the processing
    parser = argparse.ArgumentParser(prog="Process Sentinel-1", description="Creates inteferograms using Sentinel-1 datasets using Doris-RIPPL." )
    parser.add_argument("-s", "--start_date", help="Start date of processing as yyyymmdd")
    parser.add_argument("-e", "--end_date", help="End date of processing as yyyymmdd")
    parser.add_argument("-c", "--cores", help="Number of processing cores")
    parser.add_argument("-t", "--temp", help="Temp directory location", default='')
    parser.add_argument("-r", "--resampling_temp", help="Temp directory used for master image coordinates for resampling", default='')
    parser.add_argument("-ml", "--multilooking_temp", help="Temp directory used for master image coordinates for multilooking", default='')
    # Processing boundaries Options:
    geometry_group = parser.add_mutually_exclusive_group()
    geometry_group.add_argument("-a", "--aoi", help="area of interest as WKT (enclose in double-quotes if necessary)", type=str)
    geometry_group.add_argument("-f", "--file",
                    help="Shapefile of the area of interest",
                    type=str)
    parser.add_argument("-bf", "--buffer", help="Distance fo the buffer zone.", type=float, default=0.2)
   
    # Sentinel-1 data options:
    parser.add_argument("-m", "--mode",
                    help="sensor mode. Default: 'IW'", 
                    default="IW",
                    type=str)
    parser.add_argument("-p", "--prod",
                    help="product's processing level. Default: 'SLC'", 
                    default="SLC",
                    type=str)
    parser.add_argument("-pl", "--pol",
                    help="Polarization of Sentinel-1 Data. Default: 'VV'", 
                    default='VV',
                    type=str)
    parser.add_argument("-tk", "--track",
                    help="Processing track number", 
                    type=int)
    # Output options:
    parser.add_argument("-n", "--name",
                    help="Name for the output data stack", 
                    default='',
                    type=str)

    parser.add_argument("-R", "--resolution",
                    help="Pixel resolution of the output dataset.", 
                    type=int)
    

    parser.add_argument("-md", "--master_date",
                    help="Master date for the processing data track as yyyymmdd. Choose a date with the lowest coverage to create an image with ONLY the overlapping parts", 
                    default='',
                    type=str)

    args = parser.parse_args()

    # =====================================================================
    # Check validity of processing boundary when using -f or --file option
    # =====================================================================
    if args.file is not None:
        extension = pathlib.Path(args.file).suffix
        if extension == ".shp":
            geo_ = utils.read_shapefile(args.file)
            if len(geo_) == 1:
                args.aoi = geo_[0].wkt  
            else:
                RuntimeError("The file must contain a single geometry")
        elif extension == ".kml":
            geo_ = utils.read_kml(args.file)
            if len(geo_) == 1:
                args.aoi = geo_[0].wkt  
            else:
                RuntimeError("The file must contain a single geometry")
        else:
            raise TypeError("File extension not supported. Use '.shp' or '.kml' ")

    processing_boundary = ReadWriteShapes()  # takes SHP, KML, or WKT
    if args.aoi is None:
        # This expects the file to be in the doris-rippl data directory
        processing_boundary(args.file)
    else:
        processing_boundary(args.aoi)
     
    study_area_shape = processing_boundary.shape.buffer(args.buffer)

    # =====================================================================
    # Processing inputs and outputs
    # =====================================================================
    # Inputs:
    start_date = datetime.datetime.strptime(args.start_date, '%Y%m%d')
    print('start date is ' + str(start_date.date()))
    end_date = datetime.datetime.strptime(args.end_date, '%Y%m%d')
    print('start date is ' + str(end_date.date()))
    master_date = datetime.datetime.strptime(args.master_date, '%Y%m%d')

    no_processes = int(args.cores)
    print('running code with ' + str(no_processes) + ' cores.')

    mode = args.mode
    product_type = args.prod
    polarisation = [args.pol]
    pixel_resolution = args.resolution

    track_no = args.track  # manu: track == strips of data, A track make a selection of datasets that belongs to a AoI. Images are stack, and process should keep products separated by tracks. User provides the track number.
    stack_name = args.name # 'Benelux_track_37'

    # For every track we have to select a master date. This is based on the search results earlier.
    # Choose the date with the lowest coverage to create an image with only the overlapping parts.
    # master_date = datetime.datetime(year=2020, month=3, day=28) # manu:  should be define by the user
    # =====================================================================
    # Temporary directories
    # =====================================================================

    # Define temporary directories
    tmp_directory = args.temp
    resampling_tmp_directory = args.resampling_temp
    if resampling_tmp_directory == '':
        resampling_tmp_directory = tmp_directory
    ml_grid_tmp_directory = args.multilooking_temp
    if ml_grid_tmp_directory == '':
        ml_grid_tmp_directory = tmp_directory

    print('Main temp directory is ' + tmp_directory)
    print('Temp directory for resampling is ' + resampling_tmp_directory)
    print('Temp directory for multilooking is ' + ml_grid_tmp_directory)

    if not os.path.exists(tmp_directory):
        os.mkdir(tmp_directory)
    if not os.path.exists(resampling_tmp_directory):
        os.mkdir(resampling_tmp_directory)
    if not os.path.exists(ml_grid_tmp_directory):
        os.mkdir(ml_grid_tmp_directory)

    # Create the list of the 4 different stacks.
    # track_no = 37  # manu: track == strips of data, A track make a selection of datasets that belongs to a AoI. Images are stack, and process should keep products separated by tracks. User provides the track number.

    # Number of processes for parallel processing. Make sure that for every process at least 2GB of RAM is available
    # no_processes = 4


    s1_processing = GeneralPipelines(processes=no_processes)

    # TODO: what does the creat_sentinel_stack function does?
    s1_processing.create_sentinel_stack(start_date=start_date, end_date=end_date, master_date=master_date, cores=no_processes,
                                             track=track_no,stack_name=stack_name, polarisation=polarisation,
                                             shapefile=study_area_shape, mode=mode, product_type=product_type)

    # Finally load the stack itself. If you want to skip the download step later, run this line before other steps!
    s1_processing.read_stack(start_date=start_date, end_date=end_date, stack_name=stack_name)

    """
    To define the location of the radar pixels on the ground we need the terrain elevation. Although it is possible to 
    derive terrain elevation from InSAR data, our used Sentinel-1 dataset is not suitable for this purpose. Therefore, we
    download data from an external source to create a digital elevation model (DEM). In our case we use SRTM data. 

    However, to find the elevation of the SAR data grid, we have to resample the data to the radar grid first to make it
    usable. This is done in the next steps.
    """

    # Some basic settings for DEM creation.
    dem_buffer = 0.1  # Buffer around radar image where DEM data is downloaded
    dem_rounding = 0.1  # Rounding of DEM size in degrees
    dem_type = 'SRTM1'  # DEM type of data we download (SRTM1, SRTM3 and TanDEM-X are supported)

    # Define both the coordinate system of the full radar image and imported DEM
    s1_processing.create_radar_coordinates()
    s1_processing.create_dem_coordinates(dem_type=dem_type)

    # TODO: The API for downloading doesn't work. This needs to be fix
    # Download external DEM
    s1_processing.download_external_dem(dem_type=dem_type, buffer=dem_buffer, rounding=dem_rounding,
                                        n_processes=no_processes)
    """
    Using the obtained elevation model the exact location of the radar pixels in cartesian (X,Y,Z) and geographic (Lat/Lon)
    can be derived. This is only done for the master or reference image. This process is referred to as geocoding.

    """

    # Geocoding of image
    s1_processing.geocoding()

    """
    The information from the geocoding can directly be used to find the location of the master grid pixels in the slave
    grid images. This process is called coregistration. Because the orbits are not exactly the same with every satellite 
    overpass but differ hundreds to a few thousand meters every overpass, the grids are slightly shifted with respect to 
    each other. These shift are referred to as the spatial baseline of the images. To correctly overlay the master and slave
    images the software coregisters and resamples to the master grid.

    To do so the following steps are done:
    1. Coregistration of slave to master image
    2. Deramping the doppler effects due to TOPs mode of Sentinel-1 satellite
    3. Resampling of slave image
    4. Reramping resampled slave image.

    Due to the different orbits of the master and slave image, the phase of the radar signal is also shifted. We do not 
    know the exact shift of the two image, but using the geometry of the two images we can estimate the shift of the phase
    between different pixels. Often this shift is split in two contributions:
    1. The flat earth phase. This phase is the shift in the case the earth was a perfect ellipsoid
    2. The topographic phase. This is the phase shift due to the topography on the ground.
    In our processing these two corrections are done in one go.
    """

    # Next step applies resampling and phase correction in one step.
    # Polarisation

    # Because with the geometric coregistrtation we load the X,Y,Z files of the main image for every calculation it can
    # be beneficial to load them to a fast temporary disk. (If enough space you should load them to memory disk)
    s1_processing.geometric_coregistration_resampling(polarisation=polarisation, output_phase_correction=True,
                                                      coreg_tmp_directory=resampling_tmp_directory,
                                                      tmp_directory=tmp_directory, baselines=False,
                                                      height_to_phase=True)
    
    if os.path.exists(resampling_tmp_directory):
        shutil.rmtree(resampling_tmp_directory)
    os.mkdir(resampling_tmp_directory)
    if os.path.exists(tmp_directory):
        shutil.rmtree(tmp_directory)
    os.mkdir(tmp_directory)

    """
    Now we can create calibrated amplitudes, interferograms and coherences.
    """

    # Load the images in blocks to temporary disk (or not if only coreg data is loaded to temp disk)
    temporal_baseline = 60
    min_timespan = temporal_baseline * 2
    # Every process can only run 1 multilooking job. Therefore, in the case of amplitude calculation the number of processes
    # is limited too the number of images loaded.
    amp_processing_efficiency = 1
    effective_timespan = np.maximum(no_processes * 6 * amp_processing_efficiency, min_timespan)

    no_days = datetime.timedelta(days=int(effective_timespan / 2))
    if no_days < (end_date - start_date):
        step_date = start_date
        step_dates = []
        while step_date < end_date:
            step_dates.append(step_date)
            step_date += no_days
        step_dates.append(end_date)

        start_dates = step_dates[:-2]
        end_dates = step_dates[2:]
    else:
        end_dates = [end_date]
        start_dates = [start_date]

    if not isinstance(polarisation, list):
        pol = [polarisation]
    else:
        pol = polarisation

    for start_date, end_date in zip(start_dates, end_dates):
        # manu: stack all images (includind diffent dates)
        s1_processing.read_stack(start_date=start_date, end_date=end_date, stack_name=stack_name)
        # We split the different polarisation to limit the number of files in the temporary folder.
        for p in pol: # manu: define polariation. TODO: user should control type of polarization
            for dx, dy in zip([pixel_resolution], [pixel_resolution]): 
                # The actual creation of the calibrated amplitude images
                s1_processing.create_ml_coordinates(standard_type='oblique_mercator', dx=dx, dy=dy, buffer=0,
                                                    rounding=0)
                s1_processing.prepare_multilooking_grid(p)
                s1_processing.create_calibrated_amplitude_multilooked(p,
                                                                      coreg_tmp_directory=ml_grid_tmp_directory,
                                                                      tmp_directory=tmp_directory)
                s1_processing.create_output_tiffs_amplitude()

                s1_processing.create_ifg_network(temporal_baseline=temporal_baseline)
                s1_processing.create_interferogram_multilooked(p,
                                                               coreg_tmp_directory=ml_grid_tmp_directory,
                                                               tmp_directory=tmp_directory)
                s1_processing.create_coherence_multilooked(p, coreg_tmp_directory=ml_grid_tmp_directory,
                                                           tmp_directory=tmp_directory)

                # Create output geotiffs
                s1_processing.create_output_tiffs_coherence_ifg()

                # Create lat/lon/incidence angle/DEM for multilooked grid.
                s1_processing.create_geometry_mulitlooked(baselines=True, height_to_phase=True)
                s1_processing.create_output_tiffs_geometry()

                # Do unwrapping
                if dx in [200, 500, 1000, 2000]:
                    s1_processing.create_unwrapped_images(p)
                    s1_processing.create_output_tiffs_unwrap()

                # The coreg temp directory will only contain the loaded input lines/pixels to do the multilooking. These
                # files will be called by every process so it can be usefull to load them in memory the whole time.
                # If not given, these files will be loaded in the regular tmp folder.
                if ml_grid_tmp_directory:
                    if os.path.exists(ml_grid_tmp_directory):
                        shutil.rmtree(ml_grid_tmp_directory)
                        os.mkdir(ml_grid_tmp_directory)

            # TODO: Do wee need to compute a range here?
            for dlat, dlon in zip([0.0005, 0.001, 0.002, 0.005, 0.01, 0.02],
                                  [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]):
                # The actual creation of the calibrated amplitude images
                s1_processing.create_ml_coordinates(dlat=dlat, dlon=dlon, coor_type='geographic', buffer=0,
                                                    rounding=0)
                s1_processing.prepare_multilooking_grid(p)
                s1_processing.create_calibrated_amplitude_multilooked(p,
                                                                      coreg_tmp_directory=ml_grid_tmp_directory,
                                                                      tmp_directory=tmp_directory)
                s1_processing.create_output_tiffs_amplitude()

                s1_processing.create_ifg_network(temporal_baseline=temporal_baseline)
                s1_processing.create_interferogram_multilooked(p,
                                                               coreg_tmp_directory=ml_grid_tmp_directory,
                                                               tmp_directory=tmp_directory)
                s1_processing.create_coherence_multilooked(p, coreg_tmp_directory=ml_grid_tmp_directory,
                                                           tmp_directory=tmp_directory)

                # Create output geotiffs
                s1_processing.create_output_tiffs_coherence_ifg()

                # Create lat/lon/incidence angle/DEM for multilooked grid.
                s1_processing.create_geometry_mulitlooked(baselines=True, height_to_phase=True)
                s1_processing.create_output_tiffs_geometry()

                if dlat in [0.002, 0.005, 0.01, 0.02]:
                    s1_processing.create_unwrapped_images(p)
                    s1_processing.create_output_tiffs_unwrap()

                # The coreg temp directory will only contain the loaded input lines/pixels to do the multilooking. These
                # files will be called by every process so it can be usefull to load them in memory the whole time.
                # If not given, these files will be loaded in the regular tmp folder.
                if ml_grid_tmp_directory:
                    if os.path.exists(ml_grid_tmp_directory):
                        shutil.rmtree(ml_grid_tmp_directory)
                        os.mkdir(ml_grid_tmp_directory)
              
            if tmp_directory:
                if os.path.exists(tmp_directory):
                    shutil.rmtree(tmp_directory)
                    os.mkdir(tmp_directory)
