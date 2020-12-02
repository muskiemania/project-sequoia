import datetime
import traceback

class Basic:

    def __init__(self, person):
    
        try:
            self._data = dict(person).get('basic')
        except:
            traceback.print_exc()
        
        if self._data is None:
            self._data = {}

    @property
    def given(self):
        return self._data.get('given')

    @property
    def middle(self):
        return self._data.get('middle', '')

    @property
    def surname(self):
        return self._data.get('surname')

    @property
    def sex(self):
        return self._data.get('sex')

    @property
    def suffix(self):
        return self._data.get('suffix', '')

    def load(self, args):

        if not self.given and not args.given:
            raise ValueError('missing required \'given\'')
        if not self.surname and not args.surname:
            raise ValueError('missing required \'surname\'')
        if not self.sex and not args.sex:
            raise ValueError('missing required \'sex\'')

        self._data['given'] = args.given or self.given
        self._data['middle'] = args.middle or self.middle
        self._data['surname'] = args.surname or self.surname
        self._data['suffix'] = args.suffix or self.suffix
        self._data['sex'] = args.sex[0].upper() if args.sex else self.sex

        return self._data

    def init(self):
        return self

    @property
    def extended(self):
        _surname = self._data.get('surname')
        _given = self._data.get('given')
        _middle = self._data.get('middle')
        _suffix = self._data.get('suffix')
        _sex = self._data.get('sex')

        _output = f'{_surname.upper()}'
        if _suffix:
            _output += f' {_suffix}'

        _output += f', {_given.upper()}'
        if _middle:
            _output += f' {_middle.upper()}'

        _output += f' ({_sex.lower()})'

        return _output

           
    def __str__(self):
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        _given = self._data.get('given')
        _middle = self._data.get('middle')
        _surname = self._data.get('surname')
        _suffix = self._data.get('suffix')
        _sex = self._data.get('sex')

        _output = f'{_surname.upper()}'
        if _suffix:
            _output += f' {_suffix.upper()}'
        
        _output += f', {_given.upper()}'
        if _middle:
            _output += f' {_middle.upper()[0]}'

        _output += f' ({_sex.lower()})'

        return _output

    def __dict__(self):
        return self._data
