
import argparse
from hashlib import md5
from os import path
import os
from download import connector

import pathlib
from download import utils
from dotenv import load_dotenv
from download.s1_orbit import S1OrbitProvider

load_dotenv()
USERNAME = os.getenv('ORB_USERNAME')
PASSWORD = os.getenv('ORB_PASSWORD')
ASF_BASE_URL = os.getenv('ORB_BASE_URL')

# Positional Arguments
parser = argparse.ArgumentParser(prog="Caroline Download Engine for Orbits", description="Search and downloads orbit datasets from the SciHub facility")
subparsers = parser.add_subparsers(help="Subcommands. Options for 'man' and 'conf' the same and -a is always required.")
# conf command
parser_conf = subparsers.add_parser("conf", help="download satellite datasets using a configuration file, an .env file")
parser_conf.add_argument("start", help="start date for the search.", type=str)
parser_conf.add_argument("end", help="end date for the search.", type=str)
# Options
# geometry_group = parser_conf.add_mutually_exclusive_group()
# geometry_group.add_argument("-a", "--aoi", help="area of interest as WKT (enclose in double-quotes if necessary)", type=str)
# geometry_group.add_argument("-f", "--file",
#                     help="file descrbing an area of interest. SHP or KML",
#                     type=str)

# parser_conf.add_argument("-o", "--orbit",
#                     help="flight direction along the orbit. 'Ascending' or 'Descending'. Default: 'Ascending'", 
#                     default="Ascending",
#                     type=str)
# parser_conf.add_argument("-m", "--mode",
#                     help="sensor mode. Default: 'IW'", 
#                     default="IW",
#                     type=str)
                
# parser_conf.add_argument("-p", "--prod",
#                     help="product's processing level. Default: 'SLC'", 
#                     default="SLC",
#                     type=str)

parser_conf.add_argument("-t", "--retry",
                    help="maximun number of retries on download failures. Default: 3", 
                    default=3,
                    type=int)

# manual command
parser_manual = subparsers.add_parser("man", help="manual mode. Start download using username and password")
parser_manual.add_argument("user", help="ASF DAAC account's username", type=str)
parser_manual.add_argument("password", help="ASF DAAC account's password", type=str)
parser_manual.add_argument("start", help="start date for the search.", type=str)
parser_manual.add_argument("end", help="end date for the search.", type=str)

# Options
# geometry_group = parser_manual.add_mutually_exclusive_group()
# geometry_group.add_argument("-a", "--aoi", help="area of interest as WKT (enclose in double-quotes if necessary)", type=str)
# geometry_group.add_argument("-f", "--file",
#                     help="file descrbing an area of interest. SHP or KML",
#                     type=str)

# parser_manual.add_argument("-o", "--orbit",
#                     help="flight direction along the orbit. 'Ascending' or 'Descending'. Default: 'Ascending'", 
#                     default="Ascending",
#                     type=str)
# parser_manual.add_argument("-m", "--mode",
#                     help="sensor mode. Default: 'IW'", 
#                     default="IW",
#                     type=str)
                
# parser_manual.add_argument("-p", "--prod",
#                     help="product's processing level. Default: 'SLC'", 
#                     default="SLC",
#                     type=str)

parser_manual.add_argument("-t", "--retry",
                    help="maximun number of retries on download failures. Default: 3", 
                    default=3,
                    type=int)






args = parser.parse_args()
print(args)


# # -f or --file option
# if args.file is not None:
#     extension = pathlib.Path(args.file).suffix
#     if extension == ".shp":
#         geo_ = utils.read_shapefile(args.file)
#         if len(geo_) == 1:
#             args.aoi = geo_[0].wkt  
#         else:
#             RuntimeError("The file must contain a single geometry")
#     elif extension == ".kml":
#         geo_ = utils.read_kml(args.file)
#         if len(geo_) == 1:
#             args.aoi = geo_[0].wkt  
#         else:
#             RuntimeError("The file must contain a single geometry")
#     else:
#         raise TypeError("File extension not supported. Use '.shp' or '.kml' ")


#Create connector
if USERNAME is not None and PASSWORD is not None:
    c = connector.Connector(USERNAME, PASSWORD, ASF_BASE_URL,  retain_auth=True)
else:
    c = connector.Connector(args.user, args.password, ASF_BASE_URL, retain_auth=True)

c.test_connection()

# instantiate API 

search_api = S1OrbitProvider(c)

search_results=search_api.search(args.start, end_date=args.end)

search_api.download(search_results, max_retries=args.retry)

