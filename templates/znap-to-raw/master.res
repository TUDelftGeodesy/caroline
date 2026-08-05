===============================================
MASTER RESULTFILE:                      
Created by:                             G.Mulder TU Delft
DVersion:                               Version (2015) (For TOPSAR)
FFTW library:                           used
VECLIB library:                         not used
LAPACK library:                         not used
Compiled at:                            XXXXXXXX
By GUN gcc:                             XXXXXXXX
===============================================



Start_process_control
readfiles:		1
precise_orbits:		1
crop:		1
sim_amplitude:		0
master_timing:		0
oversample:		0
resample:		0
filt_azi:		0
filt_range:		0
NOT_USED:		0
End_process_control



******************************************************************* 
*_Start_readfiles:
******************************************************************* 
Volume_file:                                              dummy
Volume_ID:                                                9999
Volume_identifier:                                        dummy
Volume_set_identifier:                                    dummy
Number of records in ref. file:                           dummy
SAR_PROCESSOR:                                            Sentinel-1
SWATH:                                                    dummy
PASS:                                                     **asc_dsc**
IMAGE_MODE:                                               IW
polarisation:                                             VV
Product type specifier:                                   S1
Logical volume generating facility:                       dummy
Location and date/time of product creation:               dummy
Number_of_lines_Swath:                                    **n_az_pixels**
number_of_pixels_Swath:                                   **n_r_pixels**
rangePixelSpacing:                                        **r_pixel_spacing**
azimuthPixelSpacing:                                      **az_pixel_spacing**
total_Burst:                                              9999
Burst_number_index:                                       9999
RADAR_FREQUENCY (HZ):                                     **radar_frequency**
Scene identification:                                     Orbit: 9999
Scene location:                                           dummy
Sensor platform mission identifer:                        S1
Scene_center_heading:                                     9999
Scene_centre_latitude:                                    **centre_latitude**
Scene_centre_longitude:                                   **centre_longitude**
Radar_wavelength (m):                                     **wavelength**
Azimuth_steering_rate (deg/s):                            9999
Pulse_Repetition_Frequency_raw_data(TOPSAR):              9.999000000000000e+03
First_pixel_azimuth_time (UTC):                           **first_pixel_az_time**
Pulse_Repetition_Frequency (computed, Hz):                **PRF_hz**
Azimuth_time_interval (s):                                **azimuth_time_interval_s**
Total_azimuth_band_width (Hz):                            **azimuth_bandwidth_hz**
Weighting_azimuth:                                        Hamming
Range_time_to_first_pixel (2way) (ms):                    **range_2way_time_to_first_pixel_ms**
Range_sampling_rate (computed, MHz):                      **range_sampling_rate_mhz**
Total_range_band_width (MHz):                             **range_bandwidth_mhz**
Weighting_range:                                          Hamming
DC_reference_azimuth_time:                                2000-Jan-01 00:00:00.000000
DC_reference_range_time:                                  9999
Xtrack_f_DC_constant (Hz, early edge):                    9999
Xtrack_f_DC_linear (Hz/s, early edge):                    9999
Xtrack_f_DC_quadratic (Hz/s/s, early edge):               9999
FM_reference_azimuth_time:                                2000-Jan-01 00:00:00.000000
FM_reference_range_time:                                  9999
FM_polynomial_constant_coeff (Hz, early edge):            9999
FM_polynomial_linear_coeff (Hz/s, early edge):            9999
FM_polynomial_quadratic_coeff (Hz/s/s, early edge):       9999
Datafile:                                                 dummy.tiff
Dataformat:                                               tiff
Number_of_lines_original:                                 **n_az_pixels**
Number_of_pixels_original:                                **n_r_pixels**
Scene_ul_corner_latitude:                                 9999
Scene_ur_corner_latitude:                                 9999
Scene_lr_corner_latitude:                                 9999
Scene_ll_corner_latitude:                                 9999
Scene_ul_corner_longitude:                                9999
Scene_ur_corner_longitude:                                9999
Scene_lr_corner_longitude:                                9999
Scene_ll_corner_longitude:                                9999
deramp:                                                   0
reramp:                                                   0
ESD_correct:                                              0
First_line (w.r.t. output_image):                         **first_az**
Last_line (w.r.t. output_image):                          **last_az**
First_pixel (w.r.t. output_image):                        **first_range**
Last_pixel (w.r.t. output_image):                         **last_range**
Number_of_pixels_output_image:                            **n_r_pixels**
Number_of_lines_output_image:                             **n_az_pixels**
******************************************************************* 
* End_readfiles:_NORMAL
******************************************************************* 



******************************************************************* 
*_Start_precise_orbits:
******************************************************************* 
 t(s)    X(m)                 Y(m)                 Z(m)                
NUMBER_OF_DATAPOINTS:       **num_data_points_orbit**
**orbit_grid**
******************************************************************* 
* End_precise_orbits:_NORMAL
******************************************************************* 



******************************************************************* 
*_Start_crop:
******************************************************************* 
Data_output_file:                          dummy.raw
Data_output_format:                        dummy
First_line (w.r.t. original_image):        **first_az**
Last_line (w.r.t. original_image):         **last_az**
First_pixel (w.r.t. original_image):       **first_range**
Last_pixel (w.r.t. original_image):        **last_range**
******************************************************************* 
* End_crop:_NORMAL
******************************************************************* 
