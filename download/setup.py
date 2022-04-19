# standard library
from setuptools import setup, find_packages

# local library
import download


# setup
install_requires = ['python-dotenv','requests', 'shapely', 'fiona', 'gdal' ]


setup(
    name="download",
    version=download.__version__,
    author="Caroline Developer Team, TU Delft",
    author_email="",
    packages=find_packages(include=['download', 'download.*']),
    install_requires=install_requires,
    description="Data donwload component for the Caroline System",
    classifiers=["Programming Language :: Python :: 3",
                 "Operating System :: OS Independent", ],
    python_requires='>=3.8',)
