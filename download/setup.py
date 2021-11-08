# standard library
from setuptools import setup, find_packages

# local library
import download


# setup
install_requires = ['requests', 'shapely', 'fiona', ]


setup(
    name="download",
    version=download.__version__,
    author="Caroline Developer Team, TU Delft",
    author_email="",
    packages=find_packages(include=['f3dasm', 'f3dasm.*']),
    install_requires=install_requires,
    description="Data donwload componentfor the Caroline System",
    classifiers=["Programming Language :: Python :: 3",
                 "Operating System :: OS Independent", ],
    python_requires='>=3.8',)
