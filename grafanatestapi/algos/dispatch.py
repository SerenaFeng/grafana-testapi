import httplib
import logging
import os

import pecan
import pkg_resources


LOG = logging.getLogger(os.path.basename(__file__))


class AlgoDispatcher(object):
    entry_points_cache = {}

    def __init__(self):
        if not AlgoDispatcher.entry_points_cache:
            for ep in pkg_resources.iter_entry_points('grafanatestapi.algos'):
                AlgoDispatcher.entry_points_cache[ep.name] = ep

    @staticmethod
    def dispatch(target, **kwargs):
        algo_type = target.pop('algo')
        LOG.info('Dispatch algo [{}]'.format(algo_type))

        entry_point = AlgoDispatcher.entry_points_cache.get(algo_type)
        if not entry_point:
            pecan.abort(status_code=httplib.BAD_REQUEST,
                        detail='Not supported Algo {}'.format(algo_type))

        ep = entry_point.load()
        res = ep().calc(target, **kwargs)
        return res
