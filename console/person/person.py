import uuid
import datetime

from person import basic, born, marriages

class Person:

    def __init__(self, _data, _index):
        self._data = _data
        self._index = _index
        self.sort_key = None
    def init(self):
        self.sort_key = str(basic.Basic(self).init())

        return self

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
    def summary(self):
        _basic = basic.Basic(self).init()
        _born = born.Born(self).init()
        _dead = False

        _summary = str(_basic)
        
        if _dead:
            _summary += f' ({_born.year}-{_dead.year})'
        if not _dead:
            _summary += f' ({_born.year}-)'
        
        return _summary

    def __str__(self):

        _born = born.Born(self).init()
        _marriages = marriages.Marriages(self).init()
        _body = ', '.join([str(i) for i in [_born, _marriages]])

        return '\n'.join([self.summary, _body])

    def __iter__(self):
        for key in self._data:
            yield key, self._data[key]
        return self._data
