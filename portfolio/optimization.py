"""MC1-P2: Optimize a portfolio."""

import pandas as pd
import numpy as np
import scipy.optimize as spo
from util import get_data, plot_data
from analysis import get_portfolio_value, get_portfolio_stats


def sharpe_maximizer(allocs, prices):
    """Optimization function to be passed to the optimizer.
    
    Parameters
    ----------
        prices: daily prices for each stock in portfolio
        allocs: Allocation for each portfolio component
    
    Returns
    -------
        sharpe_ratio: Negative sharpe ratio so the minimizer finds the maximum
    
    """
    #Get portfolio value
    port_val = get_portfolio_value(prices, allocs)
    #Get portfolio statistics
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(port_val)
    
    return -sharpe_ratio
    
    
def find_optimal_allocations(prices):
    """Find optimal allocations for a stock portfolio, optimizing for Sharpe ratio.

    Parameters
    ----------
        prices: daily prices for each stock in portfolio

    Returns
    -------
        allocs: optimal allocations, as fractions that sum to 1.0
    """

    #Initial guess, equally weighted portfolio
    init_guess = np.ones(prices.shape[1], dtype=np.float64) * 1.0 / prices.shape[1]
    alloc_bounds = [(0, prices.shape[1])] * 4
    alloc_constraint = ({ 'type': 'eq', 'fun': lambda x: np.sum(x) - 1 })
    min_result = spo.minimize(sharpe_maximizer, init_guess, args = (prices, ), 
                              method='SLSQP', options={'disp:': True}, 
                                bounds = alloc_bounds, constraints = alloc_constraint)
                                
    print min_result #Print optimization results
    return min_result.x


def optimize_portfolio(start_date, end_date, symbols):
    """Simulate and optimize portfolio allocations."""
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(start_date, end_date)
    prices_all = get_data(symbols, dates)  # automatically adds SPY
    prices = prices_all[symbols]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # Get optimal allocations
    allocs = find_optimal_allocations(prices)
    allocs = allocs / np.sum(allocs)  # normalize allocations, if they don't sum to 1.0

    # Get daily portfolio value (already normalized since we use default start_val=1.0)
    port_val = get_portfolio_value(prices, allocs)

    # Get portfolio statistics (note: std_daily_ret = volatility)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(port_val)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Optimal allocations:", allocs
    print "Sharpe Ratio:", sharpe_ratio
    print "Volatility (stdev of daily returns):", std_daily_ret
    print "Average Daily Return:", avg_daily_ret
    print "Cumulative Return:", cum_ret

    # Compare daily portfolio value with normalized SPY
    normed_SPY = prices_SPY / prices_SPY.ix[0, :]
    df_temp = pd.concat([port_val, normed_SPY], keys=['Portfolio', 'SPY'], axis=1)
    plot_data(df_temp, title="Daily Portfolio Value and SPY")


def test_run():
    """Driver function."""
    # Define input parameters
    start_date = '2010-01-01'
    end_date = '2010-12-31'
    symbols = ['GOOGL', 'AAPL', 'GLD', 'XOM']  # list of symbols
    
    # Optimize portfolio
    optimize_portfolio(start_date, end_date, symbols)


if __name__ == "__main__":
    test_run()
