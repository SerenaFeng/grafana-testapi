from datetime import datetime
import httplib
import json
import os
import time

import pecan
import requests
from six.moves.urllib import parse
from webob.exc import status_map


def url_join(*urls):
    def _path_join(base, url):
        if not base.endswith('/'):
            base += '/'
        return parse.urljoin(base, url)

    urls = (os.getenv('TESTAPI_URL', 'http://localhost:8000/api/v1'),) + urls
    return reduce(_path_join, urls)


def url_query(resource, queries):
    return url_join(resource) + '?' + parse.urlencode(queries)


def get_resources(url):
    try:
        res = requests.get(url)
        if res.status_code != httplib.OK:
            pecan.abort(res.status_code, detail=res.reason)
        return res.json()
    except Exception:
        pecan.abort(httplib.SERVICE_UNAVAILABLE)


def parse_time(date_string):
    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    return time.mktime(dt.timetuple()) * 1000


def parse_results(target, range):
    queries = json.loads(target)
    queries.update({'from': range.get('from'),
                    'to': range.get('to')})

    res = get_resources(url_query('results', queries)).get('results')
    news = [[1 if result.get('criteria') == 'PASS' else 0,
             parse_time(result.get('start_date'))] for result in res]
    return news


def search_by_url(url, resource):
    elements = get_resources(url).get(resource)
    return [element.get('name') for element in elements]


def search_elements(resource):
    return search_by_url(url_join(resource), resource)


def search_cases():
    def _by_project(project):
        url = url_join('projects', project, 'cases')
        return search_by_url(url, 'testcases')

    projects = search_elements('projects')

    cases = []
    for project in projects:
        cases.extend(_by_project(project))
    return cases


class RootController(object):

    @pecan.expose(generic=True)
    def index(self):
        return "Welcome To Grafana-TestAPI"

    @pecan.expose(generic=True, template="json")
    def query(self):
        targets = pecan.request.json.get('targets')
        range = pecan.request.json.get('range')
        rets = [
            {
                "target": target.get('target'),
                "datapoints": parse_results(target.get('target'), range)
            } for target in targets
        ]
        return rets

    @pecan.expose(generic=True, template="json")
    def search(self):
        target = pecan.request.json.get('target')
        if target == 'cases':
            return search_cases()
        else:
            return search_elements(target)

    @pecan.expose("error.html")
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), "explanation", "")
        return dict(status=status, message=message)
