#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Manuel G. Garcia
# Created Date: 06-04-2022

"""
Routines and wrappers for the creation of interferograms using Doris-RIPPL
"""

import os
import shutil
from rippl.processing_templates.general_sentinel_1 import GeneralPipelines


def run_amplitude_interferogram_coherance(pipeline, resolution, temporal_base: int, polarisation:str, crs_type:str,  temp_dir:str, grid_dir:str ) -> None:
    """ Creates calibrated amplitude, interferogram and coherance images from Sentinel-1 datasets.
    Args:
        pipeline (GeneralPipelines): intance of GeneralPipeline with preprocessed steps.
        resolution (number): resolution for the output images.
        temporal_base (int): temporal baseline.
        polarisation (str): data polarisation.
        crs_type (str): type of coordinate reference system. Accepted values 'geographic', 'oblique_mercator'.
        temp_dir (str): path to temporal directory.
        grid_dir (str): path to temporal grid directory.
    """

    if not isinstance(pipeline, GeneralPipelines):
        raise TypeError(f'{pipeline} must be an instance of GeneralPipelines')

    for size_x, size_y in zip(resolution, resolution): 
        
        # Check the type of CRS
        if crs_type == 'oblique_mercator':
            pipeline.create_ml_coordinates(standard_type='oblique_mercator', dx=size_x, dy=size_y, buffer=0,
                                                rounding=0)
        elif crs_type == 'geographic':
            pipeline.create_ml_coordinates(dlat=size_x, dlon=size_y, coor_type='geographic', buffer=0,
                                            rounding=0)
        else:
            raise NotImplementedError(f'Cannot create product for coordinate system: {crs_type}')
        
        # Processing routines    
        pipeline.prepare_multilooking_grid(polarisation)
        pipeline.create_calibrated_amplitude_multilooked(polarisation,
                                                        coreg_tmp_directory=grid_dir,
                                                        tmp_directory=temp_dir)
        pipeline.create_output_tiffs_amplitude()

        pipeline.create_ifg_network(temporal_baseline=temporal_base)
        pipeline.create_interferogram_multilooked(polarisation,
                                                coreg_tmp_directory=grid_dir,
                                                tmp_directory=temp_dir)
        pipeline.create_coherence_multilooked(polarisation, coreg_tmp_directory=grid_dir, tmp_directory=temp_dir)
        # Create output geotiffs
        pipeline.create_output_tiffs_coherence_ifg()

        # Create lat/lon/incidence angle/DEM for multilooked grid.
        pipeline.create_geometry_mulitlooked(baselines=True, height_to_phase=True)
        pipeline.create_output_tiffs_geometry()

        # Create interferogram visualization plot
        # pipeline.create_plots_ifg(overwrite=True)

        # if dlat in [0.002, 0.005, 0.01, 0.02]: # manu: not required in MVP
        #     s1_processing.create_unwrapped_images(p)
        #     s1_processing.create_output_tiffs_unwrap()

        # The coreg temp directory will only contain the loaded input lines/pixels to do the multilooking. These
        # files will be called by every process so it can be usefull to load them in memory the whole time.
        # If not given, these files will be loaded in the regular tmp folder.
        if grid_dir:
            if os.path.exists(grid_dir):
                shutil.rmtree(grid_dir)
                os.mkdir(grid_dir)
        
        return None