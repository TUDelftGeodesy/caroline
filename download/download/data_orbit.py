#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Manuel G. Garcia
# Created Date: 06-12-2021

"""
Data classes for the download engine
"""

from dataclasses import asdict, dataclass, field
import dataclasses
from datetime import datetime
import os
from dotenv import load_dotenv
from abc import ABC

load_dotenv()
BASE_DIRECTORY=os.getenv('BASE_ORBIT_DIRECTORY')


@dataclass
class Orbit:
    """Clas for tracking orbit files"""

    file_name: str
    id: str
    uri: str
    product_type: str 
    # start_time: str # "2018-05-03T04:21:30.000000"
    checksum: str = None
    footprints: str = None
    base_dir: str = BASE_DIRECTORY
     #sub directories
    type_subdir: str=field(init=False) # precise or restituted
    download_directory: str=field(init=False)
    size_MB: int = None


    def __post_init__(self):

        # format product type info:
        if self.product_type == 'AUX_RESORB':
            self.type_subdir = 'restituted' + '/'
        elif self.product_type == 'AUX_POEORB':
            self.type_subdir = 'precise' + '/'
        else:
            print(self.product_type)
            raise NotImplemented(f'Type of orbit: {self.product_type} is not supported')
        self.download_directory = os.path.join(self.base_dir, 'sentinel1', self.type_subdir)
        # print(self.download_directory)


    def prepare_directory(self) -> None:
        """
        Checks if the directory where a orbit file will be stored exits. 
        If it doesn't exist, it will create all necessary directories.
        Example: sentinel1/precise/
        """

        if not isinstance(self, Orbit):
            raise TypeError("dataset most be an instance of Orbit")

        # check base directory exits:
        if not os.path.exists(self.base_dir):
            raise FileNotFoundError(f'Base directory must exists:{self.base_dir}')

        # check download directory
        if not os.path.exists(self.download_directory):
                os.mkdir(self.download_directory)



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
    product_type = 'AUX_RESORB'
    track = "10"
    
    ob = Orbit(file_name=fileName, id= id, uri=uri,product_type=product_type, size_MB=sizeMB)
    
    # pp = Product(file_name=fileName, id=id, uri=uri, track=track, size_MB=sizeMB)
            
    # p = Product(fileName, track, beamModeType, processingLevel, flightDirection, startTime, polarization, startTime, size_MB=sizeMB)
    print(ob.download_directory)

    # print(asdict(p))

    # pp.prepare_directory()




    



