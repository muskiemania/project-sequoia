import uuid
import datetime

class Person:

    @staticmethod
    def create(given_name, surname, born, sex):

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

        return {
            '_id': str(_id),
            '_ix': _ix,
            'givenName': given_name,
            'surname': surname,
            'born': _born,
            'sex': sex[0].upper()
        }
