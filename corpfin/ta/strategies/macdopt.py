# -*- coding: utf-8 -*-


from __future__ import print_function, division

from os.path import join
import logging
import time

from numpy.core.records import fromrecords

import corpfin.datasource.online as ds
from corpfin.util.config import DIRS
from corpfin.ta.strategies.macd import MACD
from corpfin.util.common import rec2csv


logger = logging.getLogger(__name__)


def opt(products):
    time_start = time.time()
    recs = []
    model = MACD()

    for product in products:
        logger.info('Start analysis of %s', product.code)
        model.product = product
        recs += opt_single(model)

    time_end = time.time()
    recs = fromrecords(recs, names=['code', 'nfast',
                                    'nslow', 'nmacd', 'revenue'])
    rec2csv(recs, join(DIRS['out'], 'opt.csv'))

    pst = time_end - time_start

    logger.info(('Total %s para combinations computed, '
           'roughly %.3f seconds, %.3f ms per calc.'),
              len(recs), pst, pst / len(recs) * 1000)

    return recs


def opt_single(model):
    recs = []

    for nfast in range(6, 24):
        for nslow in range(nfast + 5, 31):
            for nmacd in range(6, 15):
                model.nfast = nfast
                model.nslow = nslow
                model.nmacd = nmacd
                model.analyze()
                recs.append((model.product.code, nfast,
                             nslow, nmacd, model.revenue))
    return recs


def main():
    #    db = psql.get_db()
    #    product_codes = db.prepare('''SELECT p.code AS code, p.id as id
    #        FROM products p LEFT JOIN companies c ON p.company_id = c.id
    #        WHERE c.sector IS NOT NULL
    #        and p.id < 9354
    #        ORDER BY p.id''')()

    product_codes = ds.idx_components('^DJI').index
    total = len(product_codes)
    cur = 0
    products=[]

    logger.info('Start downloading of %d products.', len(product_codes))
    for code in product_codes:
        cur += 1
        try:
            product = ds.ohlc(code, 'yahoo', start=date_from, end=date_to)
        except:
            logger.warn('(%d/%d) Fail downloading %s.', cur, total, code)
            continue

        product.code = code
        products.append(product)
        logger.info('(%d/%d) Downloaded %s.', cur, total, code)

    logger.info('Download complete.')
    return opt(products)

def demo(code='AAPL', start='2003-01-01', end='2013-01-01'):

    product = ds.ohlc(code, start=start, end=end)
    product.code = code
    opt([product])


if __name__ == '__main__':

    period = 'd'
    code = 'AAPL'
    date_from = '2003-01-01'
    date_to = '2013-01-01'

    # recs = main()
    demo()
