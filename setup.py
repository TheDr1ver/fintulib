"""A collection of useful code snippets for data wrangling and analysis
"""
from setuptools import setup, find_packages

setup(
    name='fintulib',
    version='0.0.1',
    author="Anselm Schultes, Philipp Bodewig. (C) 2018 Fintu Data Science GmbH.",
    description="Fintu common data science library",
    url='https://github.com/Fintu/fintulib',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', '__pycache__']),
    include_package_data=True,

)
