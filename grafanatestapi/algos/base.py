from datetime import datetime
import httplib
import os
import time

import pecan
import requests
from six.moves.urllib import parse


def parse_time(date_string):
    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    return time.mktime(dt.timetuple()) * 1000


def url_query(resource, queries):
    return url_join(resource) + '?' + parse.urlencode(queries)


def url_join(*urls):
    def _path_join(base, url):
        if not base.endswith('/'):
            base += '/'
        return parse.urljoin(base, url)
    urls = (os.getenv('TESTAPI_URL', 'http://localhost:8000/api/v1'),) + urls
    return reduce(_path_join, urls)


class Base(object):
    def __init__(self):
        pass

    def calc(self, target, **kwargs):
        queries = target
        if 'range' in kwargs:
            range = kwargs.get('range')
            queries.update({'from': range.get('from'),
                            'to': range.get('to')})

        results = self.get_resources(url_query('results', queries)).get('results')
        return self.parse(results=results)

    def parse(self, **kwargs):
        pass

    def get_resources(self, url):
        try:
            res = requests.get(url)
            if res.status_code != httplib.OK:
                pecan.abort(res.status_code, detail=res.reason)
            return res.json()
        except Exception:
            pecan.abort(httplib.SERVICE_UNAVAILABLE)
