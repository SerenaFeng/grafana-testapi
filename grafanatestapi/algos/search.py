from grafanatestapi.algos import base


class Searcher(base.Base):
    def __init__(self):
        super(Searcher, self).__init__()

    def calc(self, target, **kwargs):
        target = target.get('target')
        if target == 'cases':
            return self.search_cases()
        else:
            return self.search_elements(target)

    def search_by_url(self, url, resource):
        try:
            elements = base.get_resources(url).get(resource)
        except:
            elements = []
        return [element.get('name') for element in elements]

    def search_elements(self, resource):
        return self.search_by_url(base.url_join(resource), resource)

    def search_cases(self):
        def _by_project(project):
            url = base.url_join('projects', project, 'cases')
            return self.search_by_url(url, 'testcases')

        projects = self.search_elements('projects')

        cases = []
        for project in projects:
            cases.extend(_by_project(project))
        return cases
