""" Pandas-specific helper functions
"""
import pandas as pd
import numpy as np
from tqdm import tqdm


def apply_on_rows_chunkwise(df, func, rows_per_chunk=300000):
    """ Apply a function over rows of a DataFrame in chunks.
    Useful to reduce memory requirements, especially if those grow non-linearly with row number.
    :df: The DataFrame to rowise apply a chunked function over
    :func: The callable function to apply on each chunk
    :rows_per_chunk: Rows per chunk. Optimize manually, for example by setting \
        such that the operation uses most of the available RAM, but does not swap.
    """
    df_results_list = []
    # TODO is there an easy way to parallelize this?
    for _, df_chunk in tqdm(df.groupby(np.arange(len(df)) // rows_per_chunk)):
        df_results_list.append(func(df_chunk))
    return pd.concat(df_results_list)
