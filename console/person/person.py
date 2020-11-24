import uuid
import datetime

from person import born

class Person:

    def __init__(self, data):
        self._data = data

    @staticmethod
    def create(given_name='', surname='', born='', sex=''):

        _id = uuid.uuid4()

        if not isinstance(given_name, str):
            raise TypeError('given_name must be a string')

        if not isinstance(surname, str):
            raise TypeError('surname must be a string')

        if not isinstance(sex, str):
            raise TypeError('sex must be a string')

        if not sex.lower() in ['m', 'male', 'f', 'female']:
            raise ValueError(f'unknown sex: {sex}')

        if not isinstance(born, str):
            raise TypeError('expecting born to be ISO date string')

        try:
            _born = datetime.datetime.fromisoformat(born)
        except:
            raise
        else:
            _born = _born.isoformat('|').split('|')[0]

        _ix = surname[0].lower()

        return Person({
            '_id': str(_id),
            '_ix': _ix,
            'givenName': given_name,
            'surname': surname,
            'born': _born,
            'sex': sex[0].upper()
        })

    def __str__(self):
        # SURNAME, GIVEN MI (YYYY-(? YYYY))
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        _surname = self._data['surname']
        _given = self._data['givenName']
        _middle = self._data.get('middle')
        _sex = self._data['sex']

        _born = born.Born(self).init()
        _dead = False

        _intro = f'{_surname.upper()}, {_given.upper()}'
        if _middle:
            _intro += f' {_middle.upper()[0]}'

        _intro += f' ({_sex.lower()})'

        if _dead:
            _intro += f' ({_born.year}-{_dead.year})'
        if not _dead:
            _intro += f' ({_born.year}-)'

        _body = ' '.join([str(i) for i in [_born]])

        return '\n'.join([_intro, _body])

    def __iter__(self):
        for key in self._data:
            yield key, self._data[key]
        return self._data
