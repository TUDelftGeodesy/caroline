""""
Download Engine for the Caroline System
"""

import os
import sys
from sys import argv, platform
from datetime import datetime
import shutil

from download import connector
from download.asf import ASF


# TODO: use argparse instead: https://stackoverflow.com/questions/41125435/passing-command-line-argument-with-whitespace-in-python
 
AOI= sys.argv[1]
START_DATE= sys.argv[2]
END_DATE= sys.argv[3]
ORBIT_DIRECTION = 'Ascending'
# ORBIT_DIRECTION = sys.argv[4] if len(sys.argv) >=5 else 'Ascending'
# SENSOR_MODE= sys.argv[5] if len(sys.argv) >= 5 else 'IW'
# PRODUCT= sys.argv[5] if len(sys.argv) > 4
# START_DATE= sys.argv[1]
print(str(sys.argv[1:]))
print(len(sys.argv))


# TODO: must use environment variables
#Create connector
c = connector.Connector("manuurs", "mEEhKTgSRhb3EHC#77yi", 'https://api.daac.asf.alaska.edu/', retain_auth=True)
c.test_connection()

# instantiate API 
search_api = ASF(c)

# search_results=search_api.search(AOI, START_DATE, END_DATE, orbit_direction=ORBIT_DIRECTION,
#         sensor_mode='IW', product='SLC', instrument_name='Sentinel-1')