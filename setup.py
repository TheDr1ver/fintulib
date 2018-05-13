"""A collection of useful code snippets for data wrangling and analysis
"""
from setuptools import setup, find_packages

setup(
    name='fintulib',
    version='0.0.3',
    author="Anselm Schultes, Philipp Bodewig. (C) 2018 Fintu Data Science GmbH.",
    description="A collection of useful code snippets for data wrangling and analysis",
    url='https://github.com/Fintu/fintulib',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', '__pycache__']),
    include_package_data=True,
    install_requires=[
        "google-cloud-storage >= 1.8.0",
        "dill >= 0.2.7.1",
        "numpy >= 1.14.2",
        "pandas >= 0.22.0",
        "protobuf >= 3.0.0",
        "scikit_learn >= 0.19.1",
        "scipy >= 1.1.0",
        "setuptools >= 39.0.1",
        "statsmodels >= 0.8.0"
    ]
)
