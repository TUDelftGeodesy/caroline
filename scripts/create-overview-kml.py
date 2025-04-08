from datetime import datetime

from caroline.config import get_config
from caroline.kml import KML, add_AoI_extent_folder, add_coregistered_stack_folder, add_SLC_folder

# this script produces an overview KML of all available data on Spider. It is called daily by create-overview-kml.sh
# It includes the extents of the SLCs, the coregistered stacks, and the AoI extents of all Caroline AoIs
# NOTE: this only accounts for Sentinel-1 AoIs and data

CONFIG = get_config()

# initialize the KML
now = datetime.now()
now_str = now.strftime("%Y%m%d")
kml = KML(f"{CONFIG['AOI_OVERVIEW_DIRECTORY']}/AoI_summary_{now_str}.kml")

# First add the SLCs
kml = add_SLC_folder(kml)

# Then the stack AoIs
kml = add_coregistered_stack_folder(kml)

# Finally, the processing AoIs
kml = add_AoI_extent_folder(kml)

# Save the KML
kml.save()
