import datetime
import traceback
import re

from helpers import location_helpers

class Specials:

    def __init__(self, person):
    
        try:
            self.__person = person
            self._data = dict(person).get('specials', {})
            self._marriages = dict(person).get('marriages', {})
            
            _consolidated = []
            _consolidated.extend(self._data.values())
            _consolidated.extend([{**old, 'name': 'MARRIAGE'} for old in self._marriages.values()])

            _get_event_date = lambda x: datetime.datetime.fromisoformat(x['on']) if 'on' in x else 0
            self._consolidated = sorted(_consolidated, key=_get_event_date)

        except:
            traceback.print_exc()

    def load(self, args):
        # operations:
        # add special (spouse + date? + location?)
        # remove special (by spouse and index)
        # edit special? (by spouse and index)
        # - add date, or location, or children

        if args.a:
            self._add_special(args)
        elif args.r:
            self._remove_special(args)
        elif args.e:
            self._edit_special(args)

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

    def _add_special(self, args):
        _ix = 9999
        _special = {
            _ix: {}
        }

        if not args.name:
            raise ValueError('name is required for new special event')

        _special[_ix]['name'] = args.name

        if args.on:
            try:
                __special = datetime.datetime.fromisoformat(args.on)
                _special[_ix]['on'] = __special.isoformat('|').split('|')[0]
            except:
                raise

        __location_helpers = location_helpers.LocationHelpers(_special[_ix]).load(args)

        if __location_helpers.venue:
            _special[_ix]['venue'] = __location_helpers.venue
        if __location_helpers.city:
            _special[_ix]['city'] = __location_helpers.city
        if __location_helpers.state:
            _special[_ix]['state'] = __location_helpers.state
        if __location_helpers.country:
            _special[_ix]['country'] = __location_helpers.country

        if args.by:
            _special[_ix]['by'] = args.by

        if args.godparent:
            _existing = list(set(_special[_ix]['godparents']))
            _existing.extend(args.godparent.split(' '))
            _special[_ix]['godparents'] = list(set(_existing))
        if args.school:
            _special[_ix]['school'] = args.school
        if args.company:
            _special[_ix]['company'] = args.company
        if args.degree:
            _special[_ix]['degree'] = args.degree

        self._data[_ix] = _special[_ix]

        return True

    def _remove_special(self, args):

        if not args.num:
            raise ValueError('special number is required to remove event')

        try:
            del self._data[args.num]
        except Exception as ex:
            raise

    def _edit_special(self, args):
    
        if not args.num:
            raise ValueError('special number is required to remove event')

        if args.on:
            try:
                __special = datetime.datetime.fromisoformat(args.on)
                self._data[args.num]['on'] = __special.isoformat('|').split('|')[0]
            except:
                raise
        
        __location_helpers = location_helpers.LocationHelpers({}).load(args)
        
        if __location_helpers.venue:
            self._data[args.num]['venue'] = __location_helpers.venue
        if __location_helpers.city:
            self._data[args.num]['city'] = __location_helpers.city
        if __location_helpers.state:
            self._data[args.num]['state'] = __location_helpers.state
        if __location_helpers.country:
            self._data[args.num]['country'] = __location_helpers.country

        if args.by:
            self._data[args.num]['by'] = args.by

        if args.godparent:
            _gp = self._data[args.num].get('godparents', [])
            _gp.extend(args.godparent)

            self._data[args.num]['godparents'] = list(set(_gp))

        if args.school:
            self._data[args.num]['school'] = args.school
        if args.company:
            self._data[args.num]['company'] = args.company
        if args.degree:
            self._data[args.num]['degree'] = args.degree

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

        _specials = self._data.values()
        get_event_date = lambda x: datetime.datetime.fromisoformat(x['on']) if 'on' in x else 0
        _specials = sorted(_specials, key=get_event_date)
        self._data = dict(enumerate(_specials, 1))

    def init(self):

        return self

    def __str__(self):
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        # LAST, FIRST (g) (YYYY-yyyy)
        #    NAME on MMM. DD, YYYY 
        #        at LOCATION
        #        in CITY?, STATE?, COUNTRY?
        #        Extra Info (i.e. 
        #        By (...)
        #        Godparents:
        #            LAST, FIRST (g) (YYYY-yyyy)

        _specials = []
        for _event in self._consolidated:
            _output = ''

            _name = _event['name']
            _output = f'  {_name.upper()}'
            
            if 'on' in _event:
                __event = datetime.datetime.fromisoformat(_event['on'])
                _event['on'] = __event.isoformat('|').split('|')[0]
                _output += ' on ' + __event.strftime('%b. %d, %Y')
            else:
                continue

            if 'by' in _event:
                _by = _event['by']
                _output += '\n' + f'    by {_by}' if _by else ''

            if 'spouse' in _event:
                _spouse_id = _event['spouse']
                _spouse_name = self.__person._index.get(_spouse_id, '')
                _spouse_name = _spouse_name.split('(')[0]
                _output += '\n' + f'    to {_spouse_name}' if _spouse_name else ''

            if 'school' in _event:
                _school = _event['school']
                _output += '\n' + f'    from {_school}' if _school else ''
            if 'company' in _event:
                _company = _event['company']
                _output += ''.join(['\n' + f'    from {_co}' for _co in _company] if _company else [])

            __location_helpers = location_helpers.LocationHelpers(_event)
            if __location_helpers.specials():
                _output += '\n' + __location_helpers.specials()

            if 'degree' in _event:
                _degrees = _event['degree']
                _output += ''.join(['\n' + f'    with {_degree}' for _degree in _degrees] if _degrees else [])

            if _name == 'BAPTISM' and 'godparents' in _event:
                _gp = [self.__person._index[id] for id in _event['godparents']]
                _birth_year = lambda x: int(re.search('\((\d{4})\-(\d{4})?\)$', x).group(1))
                _is_male = lambda x: '(m)' not in x
                _gp = sorted(_gp, key=lambda x: (_birth_year(x), _is_male(x)))
                _gp = [gp.split('(')[0] for gp in _gp]
                _output += '\n' + '    Godparents:' + '\n'
                _output += '\n'.join([f'      {gp}' for gp in _gp])


            _specials.append(_output)

        #print(_specials)
        if not _specials:
            return ''

        return '\n'.join(_specials)

    @property
    def as_list(self):
        # Born Mmm dd, YYYY (? in City (?, ST) (? (CTY))) (? to SURNAME, FATHER MI (YYYY-)) (? and  SURNAME, MOTHER MI (YYYY-))

        # LAST, FIRST (g) (YYYY-yyyy)
        #    NAME on MMM. DD, YYYY 
        #        at LOCATION
        #        in CITY?, STATE?, COUNTRY?
        #        Extra Info (i.e. 
        #        By (...)
        #        Godparents:
        #            LAST, FIRST (g) (YYYY-yyyy)

        _specials = []
        for _event in self._consolidated:
            _output = ''

            _name = _event['name']
            _output = f'  {_name.upper()}'
            
            if 'on' in _event:
                __event = datetime.datetime.fromisoformat(_event['on'])
                _event['on'] = __event.isoformat('|').split('|')[0]
                _output += ' on ' + __event.strftime('%b. %d, %Y')
            else:
                continue

            if 'by' in _event:
                _by = _event['by']
                _output += '\n' + f'    by {_by}' if _by else ''

            if 'spouse' in _event:
                _spouse_id = _event['spouse']
                _spouse_name = self.__person._index.get(_spouse_id, '')
                _spouse_name = _spouse_name.split('(')[0]
                _output += '\n' + f'    to {_spouse_name}' if _spouse_name else ''

            if 'school' in _event:
                _school = _event['school']
                _output += '\n' + f'    from {_school}' if _school else ''
            if 'company' in _event:
                _company = _event['company']
                _output += ''.join(['\n' + f'    from {_co}' for _co in _company] if _company else [])

            __location_helpers = location_helpers.LocationHelpers(_event)
            if __location_helpers.specials():
                _output += '\n' + __location_helpers.specials()

            if 'degree' in _event:
                _degrees = _event['degree']
                _output += ''.join(['\n' + f'    with {_degree}' for _degree in _degrees] if _degrees else [])

            if _name == 'BAPTISM' and 'godparents' in _event:
                _gp = [self.__person._index[id] for id in _event['godparents']]
                _birth_year = lambda x: int(re.search('\((\d{4})\-(\d{4})?\)$', x).group(1))
                _is_male = lambda x: '(m)' not in x
                _gp = sorted(_gp, key=lambda x: (_birth_year(x), _is_male(x)))
                _gp = [gp.split('(')[0] for gp in _gp]
                _output += '\n' + '    Godparents:' + '\n'
                _output += '\n'.join([f'      {gp}' for gp in _gp])


            _specials.append(_output)

        #print(_specials)
        if not _specials:
            return []

        return _specials

    def __dict__(self):
        return self._data

    def __bool__(self):
        return bool(self._data)
