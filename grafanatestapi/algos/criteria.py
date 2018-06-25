from grafanatestapi.algos import base


class Criteria(base.Base):
    def __init__(self):
        super(Criteria, self).__init__()

    def parse(self, results):
        return [[1 if result.get('criteria') == 'PASS' else 0,
                 base.parse_time(result.get('start_date'))]
                for result in results]
