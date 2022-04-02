# local library
import processing
# standard library
from setuptools import find_packages, setup



setup(
    name="processing",
    version="0.0.2",
    author="Caroline Developer Team, TU Delft",
    author_email="",
    packages=find_packages(include=['processing', 'processing.*']),
    install_requires=   ['python-dotenv', 
                        'shapely', 
                        'gdal'
                        ],
    description="Data processing component for the Caroline System",
    classifiers=["Programming Language :: Python :: 3",
                 "Operating System :: OS Independent", ],
    python_requires='>=3.8')
