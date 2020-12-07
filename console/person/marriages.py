import datetime
import traceback
import re

from helpers import location_helpers

class Marriages:

    def __init__(self, person):
    
        try:
            self.__person = person
            self._data = dict(person).get('marriages', {})

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
            self._edit_marriage(args)

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
        self.__consolidate()
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

        __location_helpers = location_helpers.LocationHelpers(_marriage[_ix]).load(args)

        if __location_helpers.venue:
            _marriage[_ix]['venue'] = __location_helpers.venue
        if __location_helpers.city:
            _marriage[_ix]['city'] = __location_helpers.city
        if __location_helpers.state:
            _marriage[_ix]['state'] = __location_helpers.state
        if __location_helpers.country:
            _marriage[_ix]['country'] = __location_helpers.country

        self._data[_ix] = _marriage[_ix]

        return True

    def _remove_marriage(self, args):

        if not args.num:
            raise ValueError('marriage number is required to remove marriage')

        if not args.spouse:
            raise ValueError('spouse is required to remove marriage')

        try:
            _marriage = self._data[args.num]
            _spouse = _marriage['spouse']
            if _spouse != args.spouse:
                raise ValueError('marriage number and spouse mismatch')
            
            del self._data[args.num]
        except Exception as ex:
            raise

    def _edit_marriage(self, args):
    
        if not args.num:
            raise ValueError('marriage number is required to remove marriage')

        if not args.spouse:
            raise ValueError('spouse is required to remove marriage')

        try:
            _marriage = self._data[args.num]
            _spouse = _marriage['spouse']
            if _spouse != args.spouse:
                raise ValueError('marriage number and spouse mismatch')
        except Exception as ex:
            raise

        if args.on:
            try:
                __marriage = datetime.datetime.fromisoformat(args.on)
                self._data[args.num]['on'] = __marriage.isoformat('|').split('|')[0]
            except:
                raise
        
        if args.divorced:
            try:
                __divorced = datetime.datetime.fromisoformat(args.divorced)
                self._data[args.num]['divorced'] = _divorced.isoformat('|').split('|')[0]
            except:
                self._data[args.num]['divorced'] = True

        if args.widowed:
            try:
                __widowed = datetime.datetime.fromisoformat(args.widowed)
                self._data[args.num]['widowed'] = _widowed.isoformat('|').split('|')[0]
            except:
                self._data[args.num]['widowed'] = True

        __location_helpers = location_helpers.LocationHelpers({}).load(args)
        
        if __location_helpers.venue:
            self._data[args.num]['venue'] = __location_helpers.venue
        if __location_helpers.city:
            self._data[args.num]['city'] = __location_helpers.city
        if __location_helpers.state:
            self._data[args.num]['state'] = __location_helpers.state
        if __location_helpers.country:
            self._data[args.num]['country'] = __location_helpers.country

        _children = set(self._data[args.num]['children'] if 'children' in self._data[args.num] else [])
        if args.children:
            _children = _children.union(set(args.children))

        _index = set([_id for (_id, _) in self.__person._index.items()])

        _children.intersection_update(_index)
        self._data[args.num]['children'] = list(_children)

        return True

    def __consolidate(self):
        # must translate:
        # 1:  { ... }
        # 3:  { ... }
        # 99: { ... }
        # 
        # to:
        # 1: { ... }
        # 2: { ... }
        # 3: { ... }
        # (where these are chronological)

        _marriages = self._data.values()
        get_wedding_date = lambda x: datetime.datetime.fromisoformat(x['on']) if 'on' in x else 0
        _marriages = sorted(_marriages, key=get_wedding_date)
        self._data = dict(enumerate(_marriages, 1))

    def init(self):

        return self

    def __str__(self):
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        _marriages = []

        for _key in sorted(self._data.keys()):
            _spouse_id = self._data[_key]['spouse']
            _spouse_name = self.__person._index[_spouse_id]
            _output = f'MARRIED to {_spouse_name}'

            if 'on' in self._data[_key]:
                __marriage = datetime.datetime.fromisoformat(self._data[_key]['on'])
                self._data[_key]['on'] = __marriage.isoformat('|').split('|')[0]
                _output += ' on ' + __marriage.strftime('%b. %d, %Y')

            __location_helpers = location_helpers.LocationHelpers(self._data[_key])
            _output += str(__location_helpers)

            if 'children' in self._data[_key]:
                # must peruse index to fetch summaries for parents, sort by sex
                _children = [self.__person._index[_id] for _id in self._data[_key]['children']]
                _birth_year = lambda x: int(re.search('\((\d{4})\-(\d{4})?\)$', x).group(1))
                _is_male = lambda x: '(m)' not in x
                _children = sorted(_children, key=lambda x: (_birth_year(x), _is_male(x)))

                if len(_children) == 1:
                    _output += f'. CHILDREN: {_children[0]}'
                if len(_children) == 2:
                    _output += f'. CHILDREN: ' + ' and '.join(_children)
                if len(_children) > 2:
                    _output += f'. CHILDREN: ' + ', '.join(_children[:-1])
                    _output += ' and ' + _children[-1]

            if 'divorced' in self._data[_key]:
                try:
                    __divorce = datetime.datetime.fromisoformat(self._data[_key]['divorced'])
                    _output += '. DIVORCED on ' + __divorce.strftime('%b. %d, %Y')
                except:
                    _output += '. DIVORCED'

            if 'widowed' in self._data[_key]:
                try:
                    __widowed = datetime.datetime.fromisoformat(self._data[_key]['widowed'])
                    _output += '. WIDOWED on ' + __widowed.strftime('%b. %d, %Y')
                except:
                    _output += '. WIDOWED'

            _marriages.append(_output)

        return '. '.join(_marriages) + '.'

    def __dict__(self):
        return self._data

    def __bool__(self):
        return bool(self._data)
