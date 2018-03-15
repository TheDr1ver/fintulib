"""Common data science functionality 


"""
from setuptools import setup, find_packages

# trick: create requirements.txt with "-e ." in it -> installs from install_requires
setup(
    name='fintulib',
    version='0.0.1',
    author="Anselm Schultes, Philipp Bodewig. (C) 2018 Fintu Data Science GmbH.",
    description="Fintu common data science library",
    url='https://gitlab.com/fintu/consulting/lib/fintulib.git',
    packages=[
        'fintulib.wrangle',
        'fintulib.common',
        'fintulib.model',
        'fintulib'
    ], # find_packages does not work https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages
    package_dir={'': 'src'},
    # do not use install_requires for now, as it interacts with requirements.txt
    # install_requires=[
    #     'numpy',
    #     'scipy',
    #     'nltk',
    #     'pandas'
    # ]
)