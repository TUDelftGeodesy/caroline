#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Manuel G. Garcia
# Created Date: 12-05-2021

"""
Custom Exceptions for the Download package
"""


class DataUnavailableError(Exception):
    """Raise when no datasets are available"""
    pass

