import json
import logging
import os

import pecan
from webob.exc import status_map

from grafanatestapi.algos.dispatch import AlgoDispatcher

LOG = logging.getLogger(os.path.basename(__file__))


class RootController(object):

    @pecan.expose(generic=True)
    def index(self):
        return "Welcome To Grafana-TestAPI"

    @pecan.expose(generic=True, template="json")
    def query(self):
        targets = pecan.request.json.get('targets')
        range = pecan.request.json.get('range')
        LOG.debug('Query targets [{}]'.format(targets))
        rets = [
            {
                "target": target.get('target'),
                "datapoints": AlgoDispatcher().dispatch(
                    json.loads(target.get('target')),
                    range=range)
            } for target in targets
        ]
        return rets

    @pecan.expose(generic=True, template="json")
    def search(self):
        target = pecan.request.json.get('target')
        LOG.info('Search target [{}]'.format(target))
        return AlgoDispatcher().dispatch({'algo': 'search',
                                          'target': target})

    @pecan.expose("error.html")
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), "explanation", "")
        return dict(status=status, message=message)
