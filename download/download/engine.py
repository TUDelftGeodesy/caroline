
import argparse
from hashlib import md5
from download import connector
from download.asf import ASF

# Positonal Arguments
parser = argparse.ArgumentParser(prog="Caroline Download Engine", description="Search and downloads Sentinel-1 datasets from the ASF DAAC facility")
parser.add_argument("user", help="ASF DAAC account's username", type=str)
parser.add_argument("password", help="ASF DAAC account's password", type=str)
parser.add_argument("aoi", help="area of interest as WNT (enclose in double-quotes if necessary)", type=str)
parser.add_argument("start", help="start date for the search.", type=str)
parser.add_argument("end", help="end date for the search.", type=str)
# Optional
parser.add_argument("-f", "--file",
                    help="shapefile of an area of interest",
                    type=str)
parser.add_argument("-o", "--orbit",
                    help="flight direction along the orbit. 'Ascending' or 'Descending'. Default: 'Ascending'", 
                    default="Ascending",
                    type=str)
parser.add_argument("-m", "--mode",
                    help="sensor mode. Default: 'IW'", 
                    default="IW",
                    type=str)
                
parser.add_argument("-p", "--prod",
                    help="product's processing level. Default: 'SLC'", 
                    default="SLC",
                    type=str)

parser.add_argument("-t", "--retry",
                    help="maximun number of retries on download failures. Default: 3", 
                    default=3,
                    type=int)


args = parser.parse_args()

#Create connector
c = connector.Connector(args.user, args.password, 'https://api.daac.asf.alaska.edu/', retain_auth=True)
c.test_connection()

# instantiate API 
search_api = ASF(c)

search_results=search_api.search(args.aoi, args.start, args.end, 
                                orbit_direction=args.orbit,
                                sensor_mode=args.mode, 
                                product=args.prod, 
                                instrument_name='Sentinel-1')

search_api.download(search_results, max_retries=args.retry)

