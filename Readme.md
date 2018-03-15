# Fintu common data science library

## Install
Check out this library, then in it's root directory use  
```
pip install -e .
```
to install in your python environment.

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