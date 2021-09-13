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
    checksum: str = None
    footprints: str = None
    tracks: int = None
    orbit_directions: str = None
    date: str = None
    polarisation: str = None