import datetime
import traceback

from helpers import location_helpers

class Married:

    def __init__(self, person):
    
        try:
            self.__person = person
            self._data = dict(person).get('married')

        except:
            traceback.print_exc()

    def load(self, args):
        # operations:
        # add marriage (spouse + date? + location?)
        # remove marriage (by spouse and index)
        # edit marriage (by spouse and index)
        # - add date, or location, or children

        if args.a:
            self._add_marriage(args)
        elif args.r:
            self._remove_marriage(args)
        elif args.e:
            self._edit_marriage

        '''
        _num = args.num

        if args.on:
            try:
                __marriage = datetime.datetime.fromisoformat(args.on)
                self._data['marriage'][_num]['on'] = __born.isoformat('|').split('|')[0]
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
        '''

        return self._data
    def _add_marriage(self, args):
        _ix = 9999
        _marriage = {
            _ix: {}
        }

        if not args.spouse:
            raise ValueError('spouse is required for new marriage')

        _marriage[_ix]['spouse'] = args.spouse

        if args.on:
            try:
                __marriage = datetime.datetime.fromisoformat(args.on)
                _marriage[_ix]['on'] = __marriage.isoformat('|').split('|')[0]
            except:
                raise
        
        __location_helpers = location_helpers.LocationHelpers({}).load(args)
        
        if __location_helpers.city:
            _marriage[_ix]['city'] = __location_helpers.city
        if __location_helpers.state:
            _marriage[_ix]['state'] = __location_helpers.state
        if __location_helpers.country:
            _marriage[_ix]['country'] = __location_helpers.country

    def _remove_marriage(self, args):
        pass

    def _edit_marriage(self, args):
        pass

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
