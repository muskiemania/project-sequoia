import datetime
import traceback
import re

from helpers import location_helpers

class Etymology:

    def __init__(self, person):
    
        try:
            self.__person = person
            self._data = dict(person).get('etymology', [])

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

        _etymology = self._data

    def init(self):

        return self

    def __str__(self):

        ############################################
        #
        # MUSKIVITCH, JENNA K (f) (yyyy-?)         *
        #   "Jenna": 4# 1 + (1+1) + 1 + (2+3+1) + 1 + (1+2) + 1 + (1+1)
        #       english for "Jenny", "Jennifer"
        #       means "fair, magical being"
        #   
        #       welsh for "Guinevere", 
        #           "Gweenhwyfar"
        #       translations: 
        #           'Gwen' (white, fair)
        #           'hwyfar' (smooth, soft)
        #       means "fair one", "white shadow"
        #
        #       greek for "Jane", "Janet"
        #       means "paradise", "little bird", 
        #           "heaven"
        #
        #       arabic/hebrew translations:
        #           "little bird"
        #
        # MUSKIVITCH, JENNA K (f) (yyyy-?)
        # Continued...
        #
        #   "Karen": 1# 1 + (3)
        #       named after late maternal 
        #       grandmother, WOLBERS, KAREN LEE 
        #       (1957-2004)
        #
        ###########################################

        _etymology = []
        for _each in self._data:
            _output = ''

            _name = _each['name']
            _type = _each['type']
            _output = f'  {_name.upper() ({_type.upper()})}:'

            for _origin in _each['origins']:
                _o = _origin['origin']

                if 'derivatives' in _origin:
                    _ders = ', '.join(_origin['derivatives'])
                    _output += '\n' + f'    {_o} for {_ders}'
                elif 'translations' in _origin:
                    _txlns = ', '.join(_origin['translations'])
                    _output += '\n' + f'    {_o} translations:'
                    _output += '\n' + f'      {_txlns}'
           
                if 'translations' in _origin and 'derivatives' in _origin:
                    _txlns = ', '.join(_origin['translations'])
                    _output += '\n' + f'    translations:'
                    _output += '\n' + f'      {_txlns}'

                if 'meaning' in _origin:
                    _means = ', '.join(_origin['meaning'])
                    _output += '\n' + f'    means {_meaning}'

                if 'notes' in _origin:
                    _notes = _origin['notes']
                    _output += '\n' + f'    {_notes}'
                    
                    if 'reference' in _origin:
                        _reference = _origin['reference']
                        _name_of_kin = self.__person._index.get(_reference, '')
                        _output += f', {_name_of_kin}'


            _etymology.append(_output)

        #print(_specials)
        if not _etymology:
            return ''

        return '\n'.join(_etymology)

    @property
    def as_list(self):

        ############################################
        #
        # MUSKIVITCH, JENNA K (f) (yyyy-?)         *
        #   "Jenna": 4# 1 + (1+1) + 1 + (2+3+1) + 1 + (1+2) + 1 + (1+1)
        #       english for "Jenny", "Jennifer"
        #       means "fair, magical being"
        #   
        #       welsh for "Guinevere", 
        #           "Gweenhwyfar"
        #       translations: 
        #           'Gwen' (white, fair)
        #           'hwyfar' (smooth, soft)
        #       means "fair one", "white shadow"
        #
        #       greek for "Jane", "Janet"
        #       means "paradise", "little bird", 
        #           "heaven"
        #
        #       arabic/hebrew translations:
        #           "little bird"
        #
        # MUSKIVITCH, JENNA K (f) (yyyy-?)
        # Continued...
        #
        #   "Karen": 1# 1 + (3)
        #       named after late maternal 
        #       grandmother, WOLBERS, KAREN LEE 
        #       (1957-2004)
        #
        ###########################################

        _etymology = []
        for _each in self._data:
            _name = _each['name']
            _type = _each['type']
            _output = [f'  {_name.upper()} ({_type.upper()}):']

            for _origin in _each['origins']:
                _o = _origin['origin']

                if 'derivatives' in _origin:
                    _ders = ', '.join(_origin['derivatives'])
                    _output.append(f'    {_o} for {_ders}')
                elif 'translations' in _origin:
                    _txlns = _origin['translations']
                    _output.append(f'    {_o} translations:')
                    for txln in _txlns:
                        _output.append(f'      {txln}')
           
                if 'translations' in _origin and 'derivatives' in _origin:
                    _txlns = _origin['translations']
                    _output.append(f'    translations:')
                    for txln in _txlns:
                        _output.append(f'      {txln}')

                if 'meaning' in _origin:
                    _meaning = ', '.join(_origin['meaning'])
                    _output.append(f'    means {_meaning}')

                if 'notes' in _origin:
                    _notes = _origin['notes']
                    
                    _text = f'    {_notes}'
                    if 'reference' in _origin:
                        _reference = _origin['reference']
                        _name_of_kin = self.__person._index.get(_reference, '')
                        _text += f', {_name_of_kin}'
                    _output.append(_text)


            _etymology.append(_output)

        #print(_specials)
        if not _etymology:
            return []

        return _etymology

    def __dict__(self):
        return self._data

    def __bool__(self):
        return bool(self._data)
