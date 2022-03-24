# standard library
import dotenv
from setuptools import setup, find_packages

# local library
import processing

# setup
install_requires = ['python-dotenv', 'doris-rippl']

setup(
    name="processing",
    version=processing.__version__,
    author="Caroline Developer Team, TU Delft",
    author_email="",
    packages=find_packages(include=['processing', 'processing.*']),
    install_requires=install_requires,
    description="Data processing component for the Caroline System",
    classifiers=["Programming Language :: Python :: 3",
                 "Operating System :: OS Independent", ],
    python_requires='>=3.8',)
