import datetime
import traceback

from helpers import location_helpers

class Died:

    def __init__(self, person):
    
        try:
            self.__person = person
            self._data = dict(person).get('died')
            self.year = None

            self.__location_helpers = None
        except:
            traceback.print_exc()

    def load(self, args):

        if not args.on and not 'on' in self._data:
            raise ValueError('missing required \'on\'')

        if isinstance(self._data, str) or self._data is None:
            self._data = {}
 
        if args.on:
            try:
                __died = datetime.datetime.fromisoformat(args.on)
                self._data['on'] = __died.isoformat('|').split('|')[0]
            except:
                raise
        
        self.__location_helpers = location_helpers.LocationHelpers(self._data).load(args)
        
        self._data['venue'] = self.__location_helpers.venue or self._data.get('venue')
        self._data['city'] = self.__location_helpers.city or self._data.get('city')
        self._data['state'] = self.__location_helpers.state or self._data.get('state')
        self._data['country'] = self.__location_helpers.country or self._data.get('country')

        return self._data

    def init(self):

        if isinstance(self._data, str):
            try:
                self.__died = datetime.datetime.fromisoformat(self._data)
            except:
                raise
            else:
                self.year = self.__died.year

        if isinstance(self._data, dict):
            _died = self._data.get('on')
            if _died:
                try:
                    self.__died = datetime.datetime.fromisoformat(_died)
                except:
                    self.__died = datetime.datetime(int(_died), 1, 1)

                self.year = self.__died.year

            self.__location_helpers = location_helpers.LocationHelpers(self._data)

        return self

    def __str__(self):
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        _output = 'DIED on ' + self.__born.strftime('%b. %d, %Y')

        _output += str(self.__location_helpers)

        return _output + '.'

    def __dict__(self):
        return self._data

    def __bool__(self):
        return bool(self._data)
