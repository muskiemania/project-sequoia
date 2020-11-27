import datetime
import traceback

from helpers import location_helpers

class Born:

    def __init__(self, person):
    
        try:
            self.__person = person
            self._data = dict(person).get('born')
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
                __born = datetime.datetime.fromisoformat(args.on)
                self._data['on'] = __born.isoformat('|').split('|')[0]
            except:
                raise
        
        self.__location_helpers = location_helpers.LocationHelpers(self._data).load(args)
        
        self._data['city'] = self.__location_helpers.city or self._data['city']
        self._data['state'] = self.__location_helpers.state or self._data['state']
        self._data['country'] = self.__location_helpers.country or self._data['country']

        self._data['parents'] = set(self._data['parents']) if 'parents' in self._data else set()
        if args.parents:
            self._data['parents'] = self._data['parents'].union(set(args.parents))

        _index = set([_id for (_id, _) in self.__person._index.items()])
        self._data['parents'].intersection_update(_index)
        self._data['parents'] = list(self._data['parents'])

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

            self.__location_helpers = location_helpers.LocationHelpers(self._data)

        return self

    def __str__(self):
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        _output = 'BORN: ' + self.__born.strftime('%b. %d, %Y')

        # city      city, ST    city (CTY)  city, ST (CTY)
        # ST                    ST (CTY)
        # CTY

        _output += str(self.__location_helpers)

        if 'parents' in self._data:
            # must peruse index to fetch summaries for parents, sort by sex
            _parents = [self.__person._index[_id] for _id in self._data['parents']]
            is_male = lambda x: '(m)' in x
            _parents = sorted(_parents, key=lambda x: (is_male(x), x), reverse=True)

            _output += ' to '
            _output += ' and '.join(_parents)

        return _output

    def __dict__(self):
        return self._data
