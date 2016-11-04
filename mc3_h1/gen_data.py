"""
template for generating data to fool learners (c) 2016 Tucker Balch
"""

import numpy as np


# this function should return a dataset (X and Y) that will work
# better for linear regresstion than random trees
def best4LinReg():
    X = np.random.normal(size=(100, 20), loc=0)
    return X, X[:, 19]


def best4RT():
    X = np.random.normal(size=(100, 4))
    #Y = 0.8 * X[:, 0] + 5.0 * X[:, 1]
    Y = np.sin(X[:, 0]) ** 2 + np.sin(X[:, 1]) ** 2 + np.sin(X[:, 2]) ** 2 + np.sin(X[:, 3]) ** 2
    #Y = X[:, 19]
    return X, Y

if __name__ == "__main__":
    print "they call me Tim."
