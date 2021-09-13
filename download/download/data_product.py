"""
Data classes for the download engine
"""

from dataclasses import dataclass


@dataclass
class Product:
    """Class for tracking products in the download engine"""

    #TODO: define attributes
    title: str
    id: str
    uri: str
    checksum: str = ''
    footprints: str = ''
    tracks: int = 0
    orbit_directions: str = ''
    date: str = ''
    polarisation: str = ''