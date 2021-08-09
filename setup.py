from setuptools import setup

setup(
    name='caroline',
    version='0.1.0',
    packages=['caroline'],
    install_requires=[
        'psycopg2',
    ],
    scripts = [
        'caroline/caroline'
    ],
)
