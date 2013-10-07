# -*- coding: utf-8 -*-
"""
This should only be used as a demonstration, as prices are not precise,
nor are properly adjusted for splits and dividends.

"""

import logging
from os.path import join

import pandas as pd
import numpy as np
# import matplotlib
# import matplotlib.dates as mdates
# import matplotlib.ticker as mticker
# import matplotlib.pyplot as plt
# import matplotlib.font_manager as font_manager

from corpfin.util.config import DIRS
from corpfin.ta.strategies.strategy import Strategy

logger = logging.getLogger(__name__)


class MACD(Strategy):

    """You have the option to change the slow, fast and signal periods used to calculate the MACD above.
    The default slow, fast and signal periods are set to 26, 12 and 9, respectively.
    Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator
    that shows the relationship between two moving averages of prices.
    The default MACD is represented as the difference between a 26-day and 12-day EMA of the price.
    A 9-day EMA of the MACD, referred to as the signal (or trigger) line,
    is plotted on top of the MACD to indicate buy/sell opportunities.
    Divergence, the difference between the MACD and the signal, is also plotted as a histogram.
    The MACD is most effective in wide-swinging trading markets.
    There are three standard ways to interprete the MACD:
    1. Crossovers: The basic MACD trading rule is to sell when the MACD falls below its signal line.
        Similarly, a buy signal occurs when the MACD rises above its signal line.
        It is also popular to buy/sell when the MACD goes above/below zero.
    2. Overbought/Oversold Conditions: The MACD is also useful as an overbought/oversold indicator.
        When the shorter moving average pulls away dramatically from the longer moving average (i.e. the MACD rises),
        it is likely that the security price is overextending and will soon return to more realistic levels.
        MACD overbought and oversold conditions exist vary from security to security.
    3. Divergences: An indication that an end to the current trend may be near occurs
        when the MACD diverges from the security. A bearish divergence occurs when the MACD
        is making new lows while prices fail to reach new lows.
        A bullish divergence occurs when the MACD is making new highs while prices fail to reach new highs.
        Both of these divergences are most significant when they occur at relatively overbought/oversold levels.
     - "Technical Analysis from A to Z" by Stephen Aechlis

    """

    def __init__(self, fast=12, slow=26, cdma=9,
                 column='close', verbose=False):

        self.nfast = fast
        self.nslow = slow
        self.nmacd = cdma
        self.column = column
        self.verbose = verbose
        self._product = None
        self.prices = None

        Strategy.__init__(self)

    @property
    def product(self):
        return self._product

    @product.setter
    def product(self, p):
        self._product = p
        self.prices = p[self.column].values
        self.date_idx = p.index
        self.p_code = p.code

    def analyze(self):
        init_asset = 1000
        prices = self.prices

        recs = {'price': prices,
                'ma_fast': pd.ewma(prices, span=self.nfast),
                'ma_slow': pd.ewma(prices, span=self.nslow),
                }

        recs['macd'] = recs['ma_fast'] - recs['ma_slow']
        recs['signal'] = pd.ewma(recs['macd'], span=self.nmacd)
        recs['hist'] = recs['macd'] - recs['signal']

        long = recs['hist'] > 0
        flags = long[1:] ^ long[:-1]
        if np.bincount(flags)[1] % 2 == 1:
            flags[-1] = not flags[-1]

        trade_price = prices[1:][flags]
        trade_price[::2] = 1 / trade_price[::2]
        self.revenue = init_asset * trade_price.prod()
        self.trade_count = len(trade_price)

        if self.verbose:
            analysis_file = join(DIRS['out'],
                                 self.p_code + '_analysis.csv')
            trans_file = join(DIRS['out'],
                              self.p_code + '_trans.csv')

            recs = pd.DataFrame(recs, index=self.date_idx)
            recs['long'] = long
            recs['trade_flag'] = np.insert(flags, 0, False)
            recs.to_csv(analysis_file)

            # trade_price = pd.Series(
            #     prices[1:][flags], index=self.date_idx[1:][flags])
            # trade_price.name = 'price'
            trade_price = prices[1:][flags]
            trades = pd.DataFrame(trade_price,
                                  index=self.date_idx[1:][flags],
                                  columns=['Price'])
            trades.index.name='Date'
            trades['Action'] = 'buy'
            trades['Action'][1::2] = 'sell'
            trades.to_csv(trans_file)

    def summary(self):
        s = ('%-4s Hist Data: %s from %s to %s;\t'
             'Trade stat: %s trades, total revenue %s')

        s = s % (self.product.code, len(self.product),
                 self.product.index[0], self.product.index[-1],
                 self.trade_count, self.revenue)
        self.desc = s

        logger.info(self.desc)

    def plot(self):
        raise NotImplementedError

    # def plot(self):
    #     colors = self.__class__.COLORS
    #     plt.rc('axes', grid=True)
    #     plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
    #
    #     text_size = 9
    #     left, width = 0.1, 0.8
    #     rect_price = [left, 0.5, width, 0.4]  #left, bottom, width, height
    #     rect_volume = [left, 0.3, width, 0.2]
    #     rect_macd = [left, 0.1, width, 0.2]
    #
    #     fig = plt.figure(facecolor='white')
    #     axes_color = '#f6f6f6'  # the axes background color
    #
    #     ax_price = fig.add_axes(rect_price, axisbg=axes_color)
    #     ax_volume = fig.add_axes(rect_volume, axisbg=axes_color, sharex=ax_price)
    #     ax_macd = fig.add_axes(rect_macd, axisbg=axes_color, sharex=ax_price)
    #
    #     # formatter for prices
    #     def to_percent(y, position):
    #         # Ignore the passed in position. This has the effect of scaling the default
    #         # tick locations.
    #         if len(self.products) == 1:
    #             return y
    #         s = str(100 * y)
    #
    #         # The percent symbol needs escaping in latex
    #         if matplotlib.rcParams['text.usetex'] == True:
    #             return s + r'$\%$'
    #         else:
    #             return s + '%'
    #
    #     formatter = mticker.FuncFormatter(to_percent)
    #
    #     ### plot the price and volume data: Open, High, Low, Close
    #     # use open, high, low, close. adjust in product class before strategy back testing.
    #     # currently it's only a vertical line that indicates the open and close price
    #     # todo: add ohlc and candle chart type.
    #     # dx = product.adj_close - product.close
    #
    #     # if there're more than one product, convert prices to percent
    #     if len(self.products) > 1:
    #         for p in self.products:
    #             p.convert_to_percent()
    #
    #
    #     # plot the main product.
    #     product = self.products[0]
    #     ax_price.set_title('%s' % product.code)
    #     open_p = product.open
    #     close_p = product.close
    #
    #     deltas = close_p - open_p
    #     up = deltas > 0
    #     ax_price.vlines(product.date[up], open_p[up], close_p[up], color='green', label='_nolegend_')
    #     ax_price.vlines(product.date[~up], open_p[~up], close_p[~up], color='red', label='_nolegend_')
    #
    #     # plot MA only if no products to compare
    #     if len(self.products) == 1:
    #         ax_price.plot(self.result[0], self.result[1], color='blue', lw=2, label='MA (%d)' % self.nfast)
    #         ax_price.plot(self.result[0], self.result[2], color='red', lw=2, label='MA (%d)' % self.nslow)
    #
    #     last = product[-1]
    #     s = '%s O:%1.2f H:%1.2f L:%1.2f C:%1.2f, V:%1.1fM Chg:%+1.2f' % (
    #         last.date.strftime('%d-%b-%Y'),
    #         last.open, last.high,
    #         last.low, last.close,
    #         last.volume * 1e-6,
    #         last.close - last.open )
    #     t4 = ax_price.text(0.3, 0.9, s, transform=ax_price.transAxes, fontsize=text_size)
    #
    #     # print the compare products
    #     for p in self.products[1:]:
    #         ax_price.plot(p.date, p.close, color=colors.pop(), lw=1, label=p.code)
    #
    #     #ax_price.set_yscale('log')
    #     ax_price.yaxis.set_major_formatter(formatter)
    #
    #
    #     # legend
    #     props = font_manager.FontProperties(size=10)
    #     leg = ax_price.legend(loc='center left', shadow=True, fancybox=True, prop=props)
    #     leg.get_frame().set_alpha(0.5)
    #
    #     # volume = (product.close * product.volume) / 1e6  # dollar volume in millions
    #     # vmax = volume.max()
    #     volume = product.volume
    #
    #     fillcolor = 'darkgoldenrod'
    #     poly = ax_volume.fill_between(product.date, volume, 0, label='Volume', facecolor=fillcolor, edgecolor=fillcolor)
    #     ax_volume.set_ylim(0, volume.max())
    #     ax_volume.set_yticks([])
    #
    #     ### compute the MACD indicator
    #     fillcolor = 'darkslategrey'
    #
    #     macd = self.result[3]
    #     ema = self.result[4]
    #     ax_macd.plot(product.date, macd, color='black', lw=2)
    #     ax_macd.plot(product.date, ema, color='blue', lw=1)
    #     ax_macd.fill_between(product.date, macd - ema, 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)
    #
    #     ax_macd.text(0.025, 0.95, 'MACD (%d, %d, %d)' % (self.nfast, self.nslow, self.nmacd), va='top',
    #         transform=ax_macd.transAxes, fontsize=text_size)
    #
    #     for ax in ax_price, ax_volume, ax_macd:
    #         if ax != ax_macd:
    #             for label in ax.get_xticklabels():
    #                 label.set_visible(False)
    #         else:
    #             for label in ax.get_xticklabels():
    #                 label.set_rotation(30)
    #                 label.set_horizontalalignment('right')
    #
    #         ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    #
    #     class MyLocator(mticker.MaxNLocator):
    #         def __init__(self, *args, **kwargs):
    #             mticker.MaxNLocator.__init__(self, *args, **kwargs)
    #
    #         def __call__(self, *args, **kwargs):
    #             return mticker.MaxNLocator.__call__(self, *args, **kwargs)
    #
    #     # at most 5 ticks, pruning the upper and lower so they don't overlap
    #     # with other ticks
    #     #ax_macd.yaxis.set_major_locator(mticker.MaxNLocator(5, prune='both'))
    #     #ax3.yaxis.set_major_locator(mticker.MaxNLocator(5, prune='both'))
    #
    #     ax_price.yaxis.set_major_locator(MyLocator(5, prune='both'))
    #     ax_macd.yaxis.set_major_locator(MyLocator(5, prune='both'))
    #
    #     # fig.savefig(path.join(CONFIG['temp_p'], 'macd.pdf'))
    #     plt.show(block=True)

    def apply(self):
        self.analyze()
        self.summary()
        # self.plot()

    def __call__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.analyze()
        return self.revenue


if __name__ == '__main__':
    from pandas.io.data import DataReader
    import corpfin.datasource.online as ds

    date_from = '2003-01-01'
    date_to = '2013-01-01'
    code = 'GOOG'

    product = ds.ohlc(code, start=date_from, end=date_to)
    product.code = code

    model = MACD(12, 26, 9, verbose=True)
    model.product = product
    model.analyze()
    model.summary()

    # From 2003-01-01 to 2013-01-01, MACD(12, 26, 9)
    # Trade stat: 154 trades, total revenue 6904.1657838
