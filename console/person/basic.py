import datetime
import traceback

class Basic:

    def __init__(self, person):
    
        try:
            self.__person = person
            self._data = dict(person).get('basic')
        except:
            traceback.print_exc()
        
        if self._data is None:
            self._data = {}

    def load(self, args):

        if not args.given:
            raise ValueError('missing required \'given\'')
        if not args.surname:
            raise ValueError('missing required \'surname\'')
        if not args.sex:
            raise ValueError('missing required \'sex\'')

        self._data['given'] = args.given
        self._data['middle'] = args.middle
        self._data['surname'] = args.surname
        self._data['sex'] = args.sex[0].upper()

        return self._data

    def init(self):
        return self

    def __str__(self):
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        _surname = self._data.get('surname')
        _given = self._data.get('given')
        _middle = self._data.get('middle')
        _sex = self._data.get('sex')

        _output = f'{_surname.upper()}, {_given.upper()}'
        if _middle:
            _output += f' {_middle.upper()[0]}'

        _output += f' ({_sex.lower()})'

        return _output

    def __dict__(self):
        return self._data
