import pecan
import httplib
from pecan import expose, request
from webob.exc import status_map
import json
import requests
from six.moves.urllib import parse
import time
from datetime import datetime


TESTAPI_URL = 'http://testresults.opnfv.org/test/api/v1'


def url_join(*urls):
    def _path_join(base, url):
        if not base.endswith('/'):
            base += '/'
        return parse.urljoin(base, url)

    urls = (TESTAPI_URL,) + urls
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


def parse_results(queries):
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
        if project.get('name') == 'functest':
            cases.extend(_by_project(project))
    return cases


class RootController(object):

    @expose(generic=True)
    def index(self):
        return "Welcome To Grafana-TestAPI"

    @expose(generic=True, template="json")
    def query(self):
        targets = request.json.get('targets')
        rets = [
            {
                "target": target.get('target'),
                "datapoints": parse_results(json.loads(target.get('target')))
            } for target in targets
        ]
        return rets

    @expose(generic=True, template="json")
    def search(self):
        target = request.json.get('target')
        if target == 'cases':
            return search_cases()
        else:
            return search_elements(target)

    @expose("error.html")
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), "explanation", "")
        return dict(status=status, message=message)
