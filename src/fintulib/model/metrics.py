import  numpy as np


# from  https://www.kaggle.com/dimitrislev/xgboost-in-python-with-rmspe
def rmspe_weights(y):
    w = np.zeros(y.shape, dtype=float)
    ind = y != 0
    w[ind] = 1./(y[ind]**2)
    return w


def RMSPE(y,yhat):
    """Root mean squared percentage error"""
    w = rmspe_weights(y)
    rmspe = np.sqrt(np.mean( w * (y - yhat)**2 ))
    return rmspe

