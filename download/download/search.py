#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Manuel G. Garcia
# Created Date: 06-12-2021

"""
This class provides a common interface for data APIs,
with search, download, and data validation functionalities.
"""

# from _typeshed import Self
from abc import ABC, abstractmethod


class DataSearch(ABC):
    """
    Abstract class for specifying DataApi's (data sources)
    """

    @abstractmethod
    def build_query(self, *argv):
        pass
    
    @abstractmethod
    def search(self, *argv):
        pass

    @abstractmethod
    def download(self, *argv):
        pass

    @abstractmethod
    def validate_download(self, *argv):
        pass

