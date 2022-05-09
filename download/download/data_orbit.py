#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Manuel G. Garcia
# Created Date: 06-12-2021

"""
Data classes for the download engine
"""

from dataclasses import  dataclass, field
import os
from dotenv import load_dotenv
from pathlib import Path

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

        # check and create dowload directory:
        directory = Path(self.download_directory)
        directory.mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':

  
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
    
    print(ob.download_directory)

    # ob.prepare_directory()




    



