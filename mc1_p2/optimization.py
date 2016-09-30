import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from util import get_data, plot_data
import scipy.optimize as spo
#from analysis import get_portfolio_value, get_portfolio_stats


def get_portfolio_stats(port_val, daily_rf=0, samples_per_year=252):
    daily_returns = (port_val - port_val.shift(1)) / port_val.shift(1)
    daily_returns = daily_returns[1:]
    cr = float(port_val[-1])/port_val[0] - 1.0
    adr = daily_returns.mean()
    sddr = daily_returns.std()
    sr = samples_per_year / np.sqrt(samples_per_year) * (adr - daily_rf) / sddr

    return cr, adr, sddr, sr


def error_func(allocs, prices):
    returns = prices / prices.ix[0]
    port_val = (returns * allocs).sum(axis=1)
    _, _, _, sr = get_portfolio_stats(port_val)
    
    return -sr
    
    
def find_optimal_allocations(prices):
    # Initializing to equal values
    init_guess = np.ones(prices.shape[1], dtype=np.float64) * 1.0 / prices.shape[1]
    alloc_bounds = [(0, prices.shape[1])] * prices.shape[1]
    alloc_constraint = ({'type': 'eq', 'fun': lambda x: 1 - np.sum(x)})
    min_result = spo.minimize(error_func,
                              init_guess,
                              args=(prices, ),
                              method='SLSQP',
                              options={'disp:': True},
                              bounds=alloc_bounds,
                              constraints=alloc_constraint)
    return min_result.x


# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def optimize_portfolio(sd=dt.datetime(2008, 1, 1),
                       ed=dt.datetime(2009, 1, 1),
                       syms=['GOOG', 'AAPL', 'GLD', 'XOM'],
                       gen_plot=False):
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # Get optimal allocations
    allocs = find_optimal_allocations(prices)
    allocs = allocs / np.sum(allocs)

    returns = prices / prices.ix[0]
    port_val = (returns * allocs).sum(axis=1)
    cr, adr, sddr, sr = get_portfolio_stats(port_val)

    # Normalize SPY values, and plot against optimal portfolio
    if gen_plot:
        normalized_SPY = prices_SPY / prices_SPY.ix[0, :]
        chart_data = pd.concat(
            [port_val, normalized_SPY], keys=['Portfolio', 'SPY'], axis=1)

        plot_data(chart_data, title="Optimal Portfolio vs SPY (Normalized)")

    return allocs, cr, adr, sddr, sr


def test_code():
    # This function WILL NOT be called by the auto grader
    # Do not assume that any variables defined here are available to your function/code
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!

    start_date = dt.datetime(2008, 1, 1)
    end_date = dt.datetime(2009, 12, 31)
    symbols = ['IBM', 'X', 'HNZ', 'XOM', 'GLD']

    # Assess the portfolio
    allocations, cr, adr, sddr, sr = optimize_portfolio(sd=start_date,
                                                        ed=end_date,
                                                        syms=symbols,
                                                        gen_plot=True)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocations
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr


if __name__ == "__main__":
    # This code WILL NOT be called by the auto grader
    # Do not assume that it will be called
    test_code()