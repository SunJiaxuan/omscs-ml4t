"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import datetime as dt
from util import get_data


def compute_portvals(orders_file="./orders/orders.csv", start_val=1000000):
    BUY_STRING = 'BUY'
    CASH_STRING = 'Cash'
    CASH_MULTIPLIER = 1.0
    DATE_STRING = 'Date'
    DATE_FORMAT = '%Y-%m-%d'
    EXEMPTED_DATE = '2011-06-15'
    ORDER_STRING = 'Order'
    SHARES_STRING = 'Shares'
    SYMBOL_STRING = 'Symbol'

    orders_df = pd.read_csv(
        orders_file,
        index_col=DATE_STRING,
        parse_dates=True,
        na_values=['nan'],
        names=[DATE_STRING, SYMBOL_STRING, ORDER_STRING, SHARES_STRING],
        skiprows=[0])

    orders_df.index = pd.to_datetime(orders_df.index, format=DATE_FORMAT)
    orders_df.index.to_series().apply(lambda x: x.date())
    orders_df.sort_index(inplace=True)

    # Fetch symbols, start and end dates from orders_df
    symbols = list(set(orders_df[SYMBOL_STRING]))
    start_date = min(orders_df.index)
    end_date = max(orders_df.index)
    date_range = pd.date_range(start_date, end_date)

    # Fetch prices for all relevant shares
    prices = get_data(symbols=symbols, dates=date_range, addSPY=False)
    prices[CASH_STRING] = pd.Series(CASH_MULTIPLIER, index=prices.index)
    prices = prices[pd.notnull(prices[symbols[0]])]

    # Trades will contain the number of trades performed on any given day
    trades_df = prices.copy()
    trades_df[trades_df != 0] = 0

    for index, row in orders_df.iterrows():
        if index != dt.datetime.strptime(EXEMPTED_DATE, DATE_FORMAT):
            dti = pd.to_datetime(index).date()
            previous_number_shares = trades_df.loc[index][row[SYMBOL_STRING]]
            shares_in_order = (float(row[SHARES_STRING]) if (
                row[ORDER_STRING].upper() == BUY_STRING) else -float(
                    row[SHARES_STRING]))
            updated_number_shares = previous_number_shares + shares_in_order
            trades_df.set_value(
                index,
                row[SYMBOL_STRING],
                updated_number_shares
            )
            cash_difference = -prices.loc[index][
                row[SYMBOL_STRING]] * shares_in_order
            trades_df.set_value(dti, CASH_STRING,
                                cash_difference + trades_df.loc[index][
                                    CASH_STRING])

    holdings_df = trades_df.copy()
    previous_date = None
    for date in date_range:
        if previous_date is None:
            for symbol in symbols:
                holdings_df.set_value(date, symbol,
                                      float(trades_df.loc[date][symbol]))
            holdings_df.set_value(date, CASH_STRING,
                                  start_val + trades_df.loc[date][CASH_STRING])
            previous_date = date
        elif date in prices.index:
            if is_overleveraged(
                holdings_df=holdings_df,
                trades_df=trades_df,
                prices=prices,
                date=date,
                previous_date=previous_date,
                symbols=symbols
            ):
                for symbol in symbols:
                    holdings_df.set_value(date, symbol,
                                          holdings_df.loc[previous_date][
                                              symbol])
                holdings_df.set_value(date, CASH_STRING,
                                      holdings_df.loc[previous_date][
                                          CASH_STRING])
            else:
                for symbol in symbols:
                    holdings_df.set_value(date, symbol, float(
                        holdings_df.loc[previous_date][symbol]) + float(
                            trades_df.loc[date][symbol]))
                holdings_df.set_value(date, CASH_STRING, float(
                    holdings_df.loc[previous_date][CASH_STRING]) + float(
                        trades_df.loc[date][CASH_STRING]))
            previous_date = date

    values = prices * holdings_df
    portvals = values.sum(axis=1)
    return portvals


def is_overleveraged(holdings_df, trades_df, prices, date, previous_date,
                     symbols):
    CASH_STRING = 'Cash'
    LEVERAGE_RATIO = 3.0
    total_stock_positions = 0
    personal_assets = 0
    for symbol in symbols:
        this_stocks_new_value = (holdings_df.loc[previous_date][symbol] + trades_df.loc[date][symbol]) * prices.loc[date][symbol]
        total_stock_positions += abs(this_stocks_new_value)
        personal_assets += this_stocks_new_value
    personal_assets += holdings_df.loc[previous_date][CASH_STRING] \
        + trades_df.loc[date][CASH_STRING]
    if total_stock_positions / personal_assets > LEVERAGE_RATIO:
        return True
    return False


def test_code():
    # this is a helper function you can use to test your code
    # note that during autograding his function will not be called.
    # Define input parameters

    orders_file = "./orders/orders.csv"
    start_value = 1000000

    # Process orders
    portvals = compute_portvals(orders_file=orders_file, start_val=start_value)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]]  # just get the first column
    else:
        "warning, code did not return a DataFrame"

    print portvals
    # Get portfolio stats
    daily_returns = portvals[1:].values / portvals[:-1] - 1
    sf = 245
    cum_ret = portvals[-1] / portvals[0] - 1
    avg_daily_ret = daily_returns.mean()
    std_daily_ret = daily_returns.std()
    sharpe_ratio = np.sqrt(sf) * avg_daily_ret / std_daily_ret

    start_date = dt.datetime(2008, 1, 1)
    end_date = dt.datetime(2008, 6, 1)
    #cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [0.2, 0.01, 0.02, 1.5]
    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = \
        [0.2, 0.01, 0.02, 1.5]

    # Compare portfolio against $SPX
    print "Date Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of SPY : {}".format(sharpe_ratio_SPY)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of SPY : {}".format(cum_ret_SPY)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of SPY : {}".format(std_daily_ret_SPY)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of SPY : {}".format(avg_daily_ret_SPY)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])


if __name__ == "__main__":
    test_code()
