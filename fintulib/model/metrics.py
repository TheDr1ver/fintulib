"""Metrics to score models not found in the modelling libraries themselves
"""
import pandas as pd
import numpy as np
from statsmodels.stats.contingency_tables import SquareTable, mcnemar

def _rmspe_weights(y):
    w = np.zeros(y.shape, dtype=float)
    ind = y != 0
    w[ind] = 1./(y[ind]**2)
    return w

# from  https://www.kaggle.com/dimitrislev/xgboost-in-python-with-rmspe
def RMSPE(y, yhat):
    """Root mean squared percentage error"""
    w = _rmspe_weights(y)
    rmspe = np.sqrt(np.mean(w * (y - yhat)**2))
    return rmspe

def MAPE(y,y_hat):
    """Mean Absolute Percentage Error"""
    return np.mean(abs((y - y_hat)/y))

def MeAPE(y,y_hat):
    """Median Absolute Percentage Error"""
    return np.median(abs((y - y_hat)/y))


def _mcnemar_p_value_cols(df, col1, col2):
    """Calculate McNemar's test on two columns of a data frame"""
    table = SquareTable.from_data(df[[col1, col2]])
    result = mcnemar(table.table)
    return result.pvalue


def mcnemar_p_value(df, sort_columns=True):
    """Calculate McNemar's test on subsequent columns of a data frame.
    
    :param df: The data frame to use.
    :param sort_columns: If true, columns will be sorted by their name before calculating McNemar's test scores.
    """
    if sort_columns:
        cols = list(df.columns.sort_values())
    else:
        cols = list(df.columns)
    pairs = list(zip(cols, cols[1:]))
    p_values = [_mcnemar_p_value_cols(df, p[0], p[1]) for p in pairs]
    return pd.DataFrame(np.array([pairs, p_values]).T, columns=["pair", "p_value"]).set_index("pair")
