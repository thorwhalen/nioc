import pandas as pd
import numpy as np


def _ensure_series(x):
    if isinstance(x, pd.DataFrame):
        return x[x.columns[0]]
    elif not isinstance(x, pd.Series):
        return pd.Series(x, name='val')
    else:
        return x


def sma_strategies(series, short_wins=range(3, 7 * 3), long_wins=range(7, 7 * 6, 7)):
    """
    Simple moving average (SMA) trading strategies for a cartesian product of window sizes.
        https://www.investopedia.com/articles/active-trading/052014/how-use-moving-average-buy-stocks.asp

    Args:
        series: series or array containing the time-series (from which returns series will be computed)
        short_wins: collection of short window sizes
        long_wins: collection of long window sizes

    Yields:
        Dicts with win sizes, market and stragegy perf, position arrays nad some stats

    >>> from pprint import pprint
    >>> stock_val_series = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 8]
    >>> it = sma_strategies(stock_val_series, [1, 2], [3, 4, 5])
    >>> pprint(next(it))
    {'lift': 4.740740740740738,
     'long_win': 3,
     'market_perf': 2.666666666666666,
     'n_position_switches': 2,
     'position': array([ 1,  1,  1, -1, -1, -1, -1,  1,  1,  1,  1,  1,  1]),
     'short_win': 1,
     'strategy_perf': 7.407407407407404}
    >>> pprint(next(it))
    {'lift': 1.125,
     'long_win': 4,
     'market_perf': 2.0,
     'n_position_switches': 2,
     'position': array([ 1,  1, -1, -1, -1, -1, -1,  1,  1,  1,  1,  1]),
     'short_win': 1,
     'strategy_perf': 3.125}
    """
    series = _ensure_series(series)
    val_name = series.name
    data = pd.DataFrame(series)
    data.dropna(inplace=True)  # TODO: Find more robust way
    data['returns'] = np.log(data[val_name] / data[val_name].shift(1))
    for short_win in short_wins:
        dd = data.copy()
        dd['short_win'] = dd[val_name].rolling(short_win).mean()
        for long_win in long_wins:
            if long_win > short_win:
                d = dd.copy()
                d['long_win'] = d[val_name].rolling(long_win).mean()
                d.dropna(inplace=True)
                d['position'] = np.where(d['short_win'] > d['long_win'], 1, -1)
                d['strategy'] = d['position'].shift(1) * d['returns']
                d.dropna(inplace=True)
                perf = np.exp(d[['returns', 'strategy']].sum())
                yield {'short_win': short_win,
                       'long_win': long_win,
                       'market_perf': perf['returns'],
                       'strategy_perf': perf['strategy'],
                       'position': d['position'].values,
                       'n_position_switches': sum(np.diff(d['position']) != 0),
                       'lift': perf['strategy'] - perf['returns']}
