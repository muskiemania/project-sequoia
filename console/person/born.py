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

    def load(self, args):

        if not args.on:
            raise ValueError('missing required \'on\'')

        if isinstance(self._data, str) or self._data is None:
            self._data = {}
 
        if args.on:
            try:
                self.__born = datetime.datetime.fromisoformat(args.on)
            except:
                raise
        
        self._data['on'] = self.__born.isoformat('|').split('|')[0]

        if args.city:
            self.__city = args.city
            self._data['city'] = self.__city
        if args.state:
            self.__state = args.state
            self._data['state'] = self.__state
        if args.country:
            self.__country = args.country
            self._data['country'] = self.__country

        return self._data

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
                self.__born = datetime.datetime.fromisoformat(_born)
                self.year = self.__born.year

            self.__city = self._data.get('city')
            self.__state = self._data.get('state')
            self.__country = self._data.get('country')
            self.__parents = self._data.get('parents')

        return self

    def __str__(self):
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        _output = 'BORN: ' + self.__born.strftime('%b. %d, %Y')

        # city      city, ST    city (CTY)  city, ST (CTY)
        # ST                    ST (CTY)
        # CTY

        if self.__city and not self.__state and not self.__country:
            _output += f' in {self.__city}'

        if self.__city and self.__state and not self.__country:
            _output += f' in {self.__city}, {self.__state}'

        if self.__city and self.__state and self.__country:
            _output += f' in {self.__city}, {self.__state} ({self.__country})'

        if self.__city and not self.__state and self.__country:
            _output += f' in {self.__city} ({self.__country})'

        if not self.__city and self.__state and not self.__country:
            _output += f' in {self.__state}'

        if not self.__city and self.__state and self.__country:
            _output += f' in {self.__state} ({self.__country})'

        if not self.__city and not self.__state and self.__country:
            _output += f' in {self.__country}'

        if self.__parents:

            _father = self.__parents.get('father')
            _mother = self.__parents.get('mother')
            _parents = list(filter(None, [_father, _mother]))

            if len(_parents) == 1:
                _output += ' to parent'

            if len(_parents) == 2:
                _output += f' to parent1 and parent2'
        
        return _output

    def __dict__(self):
        return self._data
