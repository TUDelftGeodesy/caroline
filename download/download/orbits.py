#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Manuel G. Garcia
# Created Date: 06-12-2021

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
parser = argparse.ArgumentParser(prog="Download Orbit files", description="Search and downloads orbit files for Sentinel 1.")
subparsers = parser.add_subparsers(help="Subcommands. Options for 'man' and 'conf' the same and -a is always required.")
# conf command
parser_conf = subparsers.add_parser("conf", help="download satellite datasets using a configuration file, an .env file")
parser_conf.add_argument("start", help="start date for the search.", type=str)
parser_conf.add_argument("end", help="end date for the search.", type=str)

# Options
parser_conf.add_argument("-ot", "--type", 
                    help="orbit type. E.g., RES = restituted, POE = precise. Default: RES ", 
                    default='RES', 
                    type=str)
parser_conf.add_argument("-t", "--retry",
                    help="maximun number of retries on download failures. Default: 3", 
                    default=3,
                    type=int)

# manual command
parser_manual = subparsers.add_parser("man", help="manual mode. Start download by providing username and password")
parser_manual.add_argument("user", help="ASF DAAC account's username", type=str)
parser_manual.add_argument("password", help="ASF DAAC account's password", type=str)
parser_manual.add_argument("start", help="start date for the search.", type=str)
parser_manual.add_argument("end", help="end date for the search.", type=str)

# Options
parser_manual.add_argument("ot", "--type", 
                    help="orbit type. E.g., RES = restituted, POE = precise. Default: RES ", 
                    default='RES', 
                    type=str)
parser_manual.add_argument("-t", "--retry",
                    help="maximun number of retries on download failures. Default: 3", 
                    default=3,
                    type=int)


args = parser.parse_args()

#Create connector
if USERNAME is not None and PASSWORD is not None:
    c = connector.Connector(USERNAME, PASSWORD, ASF_BASE_URL,  retain_auth=True)
else:
    c = connector.Connector(args.user, args.password, ASF_BASE_URL, retain_auth=True)

c.test_connection()

# instantiate API 
search_api = S1OrbitProvider(c)

# convert date format to YYYYMMDD
# This is required when used in combination with
# Doris-Rippl
start_date = utils.convert_to_dashed_date(args.start)
end_date = utils.convert_to_dashed_date(args.end)

search_results=search_api.search(start_date=start_date, end_date=end_date, osvtype=args.type)

search_api.download(search_results, max_retries=args.retry)

