#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Manuel G. Garcia
# Created Date: 06-12-2021

"""
Data classes for the download engine
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIRECTORY=os.getenv('BASE_DATA_DIRECTORY')

@dataclass
class Product:
    """Class for tracking products in the download engine"""

    file_name: str
    id: str
    uri: str
    track: str  # track number, e.g.: 37 _> t037
    beam_mode: str  # e.g.: IW
    processing_level: str # e.g. SLC
    orbit_direction: str  # e.g. ASC or DSC # small caps
    polarisation: str # e.g. VV+VH
    start_time: str # "2018-05-03T04:21:30.000000"
    checksum: str = None
    footprints: str = None
    base_dir: str = BASE_DIRECTORY
    #sub directories
    track_subdir: str = field(init=False)
    type_subdir: str = field(init=False)
    date_subdir: str = field(init=False)
    download_directory: str=field(init=False)
    size_MB: int = None

    def __post_init__(self):

        # format track info
        if int(self.track) < 10:
            formatted_track = '00' + self.track
        elif int(self.track) < 100:
            formatted_track = '0' + self.track
        else:
            formatted_track = self.track

        # format  orbit info:
        if self.orbit_direction == 'ASCENDING':
            self.orbit_direction = 'ASC'
        elif self.orbit_direction == 'DESCENDING':
            self.orbit_direction = 'DSC'
        elif self.orbit_direction == 'ASC' or self.orbit_direction == 'DSC':
            pass
        else:
            print(self.orbit_direction)
            raise NotImplemented('Theres not conversion for this type or orbit direction')
        
        # track sub directory
        self.track_subdir = 's1_' + \
                            self.orbit_direction.lower() + \
                            '_t' + formatted_track + '/'
        # type sub  dicrectory
        location_1S = self.id.find('_1S')
        class_n_polarization = self.id[location_1S+1 : location_1S+5]
        self.type_subdir = self.beam_mode + '_' + self.processing_level + '__' + class_n_polarization + '_' + self.polarisation.replace('+', '') + '/'     
        # date  sub direcotry
        self.date_subdir=self.date_(self.start_time) + '/'
        self.download_directory = os.path.join(self.base_dir, self.track_subdir, self.type_subdir, self.date_subdir)


    def date_(self, datetime_string):
        """Extract date from start_time string and formatted as YYYMMDD"""

        date_object = datetime.strptime(self.start_time, "%Y-%m-%dT%H:%M:%S.%f")
        return date_object.strftime('%Y%m%d')

    def prepare_directory(self) -> None:
        """
        Checks if the directory where a DataSet will be stored exits. 
        If it doesn't exist it will create all necessary directories.
        Example: sentinel1/s1_dsc_t037/IW_SLC__1SDV_VVVH/20210703
        Args: 
            dataset (DataSet): instance of DataSet clas
        """
        
        if not isinstance(self, Product):
            raise TypeError("dataset most be an instance of Product")

        # check base directory exits:
        if not os.path.exists(self.base_dir):
            raise FileNotFoundError(f'Base directory must exists:{self.base_dir}')

        # check for track directory
        track_directory = self.base_dir + '/' + self.track_subdir
        if not os.path.exists(track_directory):
                os.mkdir(track_directory)
        # check type directory
        type_directory = track_directory + self.type_subdir
        if not os.path.exists(type_directory):
                os.mkdir(type_directory)
        # check date directory
        date_directory = type_directory + self.date_subdir
        if not os.path.exists(date_directory):
                os.mkdir(date_directory)



if __name__ == '__main__':

    from dataclasses import asdict
    beamModeType = "IW"
    id = "S1B_IW_SLC__1SDV_20180503T042130_20180503T042158_010752_013A4C_BB7B"
    uri = 'https://some.uri.com'
    fileName = "S1B_IW_SLC__1SDV_20180503T042130_20180503T042158_010752_013A4C_BB7B.zip"
    flightDirection = "ASCENDING"
    polarization = "VV+VH"
    processingLevel = "SLC"
    sizeMB = "3619.4759950637817"
    startTime = "2018-05-03T04:21:30.000000"
    track = "10"
            
    
    pp = Product(file_name=fileName, id=id, uri=uri, track=track, beam_mode=beamModeType, processing_level=processingLevel, polarisation=polarization, orbit_direction=flightDirection, start_time=startTime, size_MB=sizeMB)
            
    # p = Product(fileName, track, beamModeType, processingLevel, flightDirection, startTime, polarization, startTime, size_MB=sizeMB)
    print(pp.download_directory)

    # print(asdict(p))

    # pp.prepare_directory()




    



