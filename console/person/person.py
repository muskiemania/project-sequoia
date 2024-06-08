import uuid
import datetime
import dateutil
import re
from person import basic, born, marriages, died, buried, images, specials

class Person:

    def __init__(self, _data, _index):
        self._data = _data
        self._index = _index
        self.sort_key = None
        self.tree = None

    def init(self):
        _basic = basic.Basic(self).init()
        _born = born.Born(self).init()
        self.sort_key = f'{_basic.surname}, {_basic.given} {_basic.middle[0] if _basic.middle else ""} ({_born.year}'

        _marriages = marriages.Marriages(self).init()
        _children = []
        for each in _marriages.data.values():
            if 'children' in each:
                _children.extend(each['children'])

        # must sort all kids alphabetically and by gender
        _birth_year = lambda x: int(re.search('\((\d{4})\-(\d{4})?\)$', x).group(1))
        _gender = lambda x: '(m)' not in x
        _children = [(_id, self._index[_id]) for _id in _children]
        _children = sorted(_children, key=lambda x: (_birth_year(x[1]), _gender(x[1])))
        self.children = [id for (id, child) in _children]

        return self

    @property
    def id(self):
        return self._data.get('_id')

    @property
    def inline_citations(self):
        return ''

    @staticmethod
    def create(given='', middle='', surname='', sex='', born='', index=None):

        _id = uuid.uuid4()

        if index is None:
            raise ValueError('index cannot be None')

        if not isinstance(given, str):
            raise TypeError('given_name must be a string')

        if not isinstance(surname, str):
            raise TypeError('surname must be a string')

        if not isinstance(sex, str):
            raise TypeError('sex must be a string')

        if not sex.lower() in ['m', 'male', 'f', 'female']:
            raise ValueError(f'unknown sex: {sex}')

        _ix = surname[0].lower()

        return Person({
            '_id': str(_id),
            '_ix': _ix,
            'basic': {
                'given': given,
                'middle': middle,
                'surname': surname,
                'sex': sex[0].upper()
            },
            'born': {
                'on': born
            }
        }, index)

    @property
    def extended(self):
        _basic = basic.Basic(self).init()
        _born = born.Born(self).init()
        _dead = died.Died(self).init()

        _summary = _basic.extended
        
        if _dead:
            _summary += f' ({_born.year}-{_dead.year})'
        if not _dead:
            _summary += f' ({_born.year}-)'
        
        return _summary

    @property
    def images(self):
        _images = images.Images(self).init()

        return _images.all(self.id)

    @property
    def summary(self):
        _basic = basic.Basic(self).init()
        _born = born.Born(self).init()
        _dead = died.Died(self).init()

        _summary = str(_basic)
        
        if _dead:
            _summary += f' ({_born.year}-{_dead.year})'
        if not _dead:
            _summary += f' ({_born.year}-)'
        
        return _summary
    
    @property
    def appendix_a(self):
        _specials = specials.Specials(self).init()

        return _specials

    @property
    def appendix_b(self):
        _born = born.Born(self).init()
        _dead = died.Died(self).init()

        _born_date = datetime.datetime(_born.year, _born.month, _born.day)
        if not _dead:
            return ''

        print(_dead)
        _died_date = datetime.datetime(_dead.year, _dead.month, _dead.day)

        _diff = dateutil.relativedelta.relativedelta(_died_date, _born_date)

        return f'{_diff.years}yr {_diff.months}mo {_diff.days}dy'

    @property
    def appendix_c(self):
        _born = born.Born(self).init()
        if _born.data.get('parents', []):
            return []

        _descendants = []
        def _traverse(level, person_id):
            #print(f'_t - level {level} + person_id {person_id}')
 
            _kids = self.tree[person_id] if person_id in self.tree else []
            #print(f'_k - {_kids}')

            for _id in _kids:
                _descendants.append((level + 1, _id))
                _traverse(level + 1, _id)

        _traverse(0, self.id)
        #print(f'i: {self.id}')

        #print(_descendants)

        _descendants = [(ix, self._index[_id]) for (ix, _id) in _descendants]
        return _descendants

    @property
    def data(self):
        return self._data

    def __str__(self):

        _born = born.Born(self).init()
        _marriages = marriages.Marriages(self).init()
        _died = died.Died(self).init()
        _buried = buried.Buried(self).init()
        _events = [_born]
        if _marriages:
            _events.append(_marriages)
        if _died:
            _events.append(_died)
        if _died and _buried:
            _events.append(_buried)
        
        return ' '.join([str(i) for i in _events])

    def __iter__(self):
        for key in self._data:
            yield key, self._data[key]
        return self._data
