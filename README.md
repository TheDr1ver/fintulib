# Fintu common data science library
This library contains some useful code snippets for data wrangling and analysis.

Note that most of the models require **Python 3**. Don't use this with **Python 2**.

## Install

### Clone repository yourself
Check out this library, then in it's root directory use  
```
pip install -e .
```
to install in your python environment.

### Using pip directly from github
You can install directly from github using pip:
```
pip install git+https://github.com/Fintu/fintulib
```

## Use  
You could import the entire package by 
```
import fintulib
``` 
or specific modules by, e.g. 
```
from fintulib import wrangle
```

### In Jupyter / Ipython
To autoreload onevery execution of a package's function, use
```
%load_ext autoreload
%autoreload 1
%aimport fintulib
```

## License

This package is licensed under MIT license.