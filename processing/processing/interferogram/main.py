#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Freek van Leijen, Manuel G. Garcia
# Created Date: 06-03-2022
""" Program to compute interferograms using Doris-RIPPL"""

import os
import argparse
import pathlib
import datetime
import shutil
import numpy as np
import processing.interferogram.routines as routines
from processing import utils
from dotenv import load_dotenv
from pathlib import Path
from rippl.processing_templates.general_sentinel_1 import GeneralPipelines
from rippl.orbit_geometry.read_write_shapes import ReadWriteShapes

# Engine General Settings:
load_dotenv()
OUTPUT_PATH = os.getenv('PRODUCTS_DIR')
TMP_DIR = os.getenv('TMP_DIR')
MULTILOOK_TMP = os.getenv('MULTILOOK_TMP')
RESAMPLING_TMP = os.getenv('RESAMPLING_TMP')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Process Interferogram", description="Creates inteferograms using Sentinel-1 datasets using Doris-RIPPL." )
    parser.add_argument("-s", "--start_date", help="Start date of processing as yyyymmdd")
    parser.add_argument("-e", "--end_date", help="End date of processing as yyyymmdd")
    parser.add_argument("-c", "--processes", help="Number of processes to use during product creation")
    parser.add_argument("-md", "--mdate",
                help="Master date for the processing data track as yyyymmdd. Choose a date with the lowest coverage to create an image with ONLY the overlapping parts", 
                default= '20200328',
                type=str)
    # Processing boundaries Options:
    geometry_group = parser.add_mutually_exclusive_group()
    geometry_group.add_argument("-a", "--aoi", help="area of interest as WKT (enclose in double-quotes if necessary)", type=str)
    geometry_group.add_argument("-f", "--file",
                    help="Shapefile of the area of interest",
                    type=str)
    parser.add_argument("-bf", "--buffer", help="Distance fo the buffer zone. Default is zero.", type=float, default=0.0)
    # Output resolution options:
    resolution_group = parser.add_mutually_exclusive_group()
    resolution_group.add_argument("-Rp", "--resplanar",
                    help="Pixel resolutions for the output datasets in planar units. A list of values (integers). E.g., 500 or 500 1000 2000. Output will use an Oblique Mercator projection.", 
                    nargs='+',
                    type=int)
    resolution_group.add_argument("-Ra", "--resarc",
                    help="Pixel resolutions for the output datasets in angular units. A list of values (integers). E.g., 1.0 or 0.1, 0.05 0.03 Output will use a Geodetic coodinate system.", 
                    nargs='+',
                    type=float)

    # Sentinel-1 data options:
    parser.add_argument("-m", "--mode",
                    help="sensor mode. Default: 'IW'", 
                    default="IW",
                    type=str)
    parser.add_argument("-p", "--proc",
                    help="product's processing level. Default: 'SLC'", 
                    default="SLC",
                    type=str)
    parser.add_argument("-pl", "--pol",
                    help="Polarization of Sentinel-1 Data. E.g. 'VV' or 'HV'. Default 'VV'", 
                    default='VV',
                    type=str)
    parser.add_argument("-tk", "--track",
                    help="Processing track number", 
                    default= 37,
                    type=int)
    # Output options:
    parser.add_argument("-n", "--name",
                    help="Name for the output data stack", 
                    default='',
                    type=str)
    

    args = parser.parse_args()

    # =====================================================================
    # Check validity of processing boundary when using -f or --file option
    # =====================================================================

    processing_boundary = ReadWriteShapes()  # takes SHP, KML, or doris-rippl-coordinate-pairs array
    if args.aoi is None:
        # This expects the file to be in the doris-rippl data directory
        # Check for valid data formats.
        extension = pathlib.Path(args.file).suffix
        if extension == ".shp":
            geo_ = utils.read_shapefile(args.file)
            if len(geo_) != 1:
               RuntimeError("Shapefile must contain a single geometry")
            else:
                processing_boundary(args.file)
        elif extension == ".kml":
            geo_ = utils.read_kml(args.file)
            if len(geo_) != 1:
               RuntimeError("KMLfile must contain a single geometry")
            else:
                processing_boundary(args.file)
        else:
            raise TypeError("File extension not supported. Must be '.shp' or '.kml' ")
    else:
        # convert WKT to doris-rippl-coordinate-pairs
        rippl_aoi = utils.wkt_to_list(args.aoi)
        processing_boundary(rippl_aoi) 

    # apply buffer to processing boundary
    study_area = processing_boundary.shape.buffer(args.buffer)

    # =====================================================================
    # Processing inputs and outputs
    # =====================================================================
    # Inputs:
    start_date = datetime.datetime.strptime(args.start_date, '%Y%m%d')
    print('start date is ' + str(start_date.date()))
    end_date = datetime.datetime.strptime(args.end_date, '%Y%m%d')
    print('start date is ' + str(end_date.date()))
    master_date = datetime.datetime.strptime(args.mdate, '%Y%m%d')

    no_processes = int(args.processes)
    print('running code with ' + str(no_processes) + ' cores.')
    
    polarisation = args.pol

    mode = args.mode
    product_type = args.proc
    track_no = args.track  # A track makes a selection of datasets that belongs to an AoI. Stacks products should be kept separated by track. User provides the track number.
    stack_name = args.name 

    # Force creation of output directory. 
    # Doris-rippl doesn't do that for some an unknown reason.
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)   

    # For every track we have to select a master date. This is based on the search results earlier.
    # =====================================================================
    # Temporary directories
    # =====================================================================

    # Define temporary directories
    tmp_directory = TMP_DIR
    resampling_tmp_directory = RESAMPLING_TMP
    if resampling_tmp_directory == '':
        resampling_tmp_directory = tmp_directory
    ml_grid_tmp_directory = MULTILOOK_TMP
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

    # =====================================================================
    # Processing Pipeline
    # =====================================================================
        # Number of processes for parallel processing. Make sure that for every process at least 2GB of RAM is available
    s1_processing = GeneralPipelines(processes=no_processes)

    # TODO: look into conflict of triggering downloading of datafiles here and in previous steps in DAG
 
    print(f'creating data stack {datetime.datetime.now()}')
    s1_processing.create_sentinel_stack(start_date=start_date, end_date=end_date, master_date=master_date, cores=no_processes,
                                             track=track_no,stack_name=stack_name, polarisation=polarisation,
                                             shapefile=study_area, mode=mode, product_type=product_type)

    print(f'reading data stack {datetime.datetime.now()}')

    # Finally load the stack itself. If you want to skip the download step later, run this line before other steps!
    s1_processing.read_stack(start_date=start_date, end_date=end_date, stack_name=stack_name)

    # Settings for DEM creation.
    dem_buffer = 0.01  # Buffer around radar image where DEM data is downloaded
    dem_rounding = 0.01  # Rounding of DEM size in degrees
    dem_type = 'SRTM1'  # DEM type of data we download (SRTM1, SRTM3 and TanDEM-X are supported)

    # Define both the coordinate system of the full radar image and imported DEM
    s1_processing.create_radar_coordinates()
    s1_processing.create_dem_coordinates(dem_type=dem_type)

    # Download external DEM
    print(f'downloading external dem {datetime.datetime.now()}')
    s1_processing.download_external_dem(dem_type=dem_type, buffer=dem_buffer, rounding=dem_rounding,
                                        n_processes=no_processes)

    # Geocoding of image
    print(f'geocoding... {datetime.datetime.now()}')
    s1_processing.geocoding()

    # Polarisation
    # Because with the geometric coregistrtation we load the X,Y,Z files of the main image for every calculation it can
    # be beneficial to load them to a fast temporary disk. (If enough space you should load them to memory)
 
    # Resampling and Phase correction
    print(f'coregistration and resampling {datetime.datetime.now()}')
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

    
    # create calibrated amplitudes, interferograms and coherences.
    # =============================================================
    temporal_baseline = 60 # manu: add as argument.. number in days (a threshold)
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

    print(f'start loop over dates {datetime.datetime.now()}')
    for start_date, end_date in zip(start_dates, end_dates):
        
        s1_processing.read_stack(start_date=start_date, end_date=end_date, stack_name=stack_name)
        # We split the different polarisation to limit the number of files in the temporary folder.
  
        # produce images based on resolution types (planar or arngular units)
        if args.resplanar is None and args.resarc is None:
            raise ValueError('Must provide a value for --resplanar or resarc. Currently None')
        if args.resplanar is not None:
            routines.run_amplitude_interferogram_coherance(s1_processing, resolution=args.resplanar, 
                temporal_base=temporal_baseline, polarisation=polarisation, crs_type='oblique_mercator', 
                temp_dir=tmp_directory, grid_dir=ml_grid_tmp_directory)
        else: # when resarc is not None
            routines.run_amplitude_interferogram_coherance(s1_processing, resolution=args.resarc, 
                temporal_base=temporal_baseline, polarisation=polarisation, crs_type='geographic', 
                temp_dir=tmp_directory, grid_dir=ml_grid_tmp_directory)

        if tmp_directory:
            if os.path.exists(tmp_directory):
                shutil.rmtree(tmp_directory)
                os.mkdir(tmp_directory)

    print(f'end loop over dates {datetime.datetime.now()}')

    print(f'end program {datetime.datetime.now()}')

