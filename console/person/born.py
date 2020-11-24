import datetime
import traceback

class Born:

    def __init__(self, person):
    
        try:
            self.__person = person
            self._data = dict(person).get('born')
            self.year = None

            self.__city = None
            self.__state = None
            self.__country = None
            self.__parents = None
        except:
            traceback.print_exc()

    def init(self):

        if isinstance(self._data, str):
            try:
                self.__born = datetime.datetime.fromisoformat(self._data)
            except:
                raise
            else:
                self.year = self.__born.year

        if isinstance(self._data, dict):
            _born = self._data.get('on')
            if _born:
                self.__born = datetime.datetime.fromisodata(_born)

            self.__city = self._data.get('city')
            self.__state = self._data.get('state')
            self.__country = self._data.get('country')
            self.__parents = self._data.get('parents')

        return self

    def __str__(self):
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        _output = 'BORN: ' + self.__born.strftime('%b. %d, %Y')

        if self.__city:
            _output += ' in {self.__city}'

        if self.__state:
            _output += ', {self.__state}'

        if self.__country:
            _output += ' ({self.__country})'

        if self.__parents:

            _father = self.__parents.get('father')
            _mother = self.__parents.get('mother')
            _parents = list(filter(None, [_father, _mother]))

            if len(_parents) == 1:
                _output += ' to parent'

            if len(_parents) == 2:
                _output += f'to parent1 and parent2'
        
        return _output

    def __dict__(self):
        return self._data
