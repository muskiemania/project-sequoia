import traceback
import us

class LocationHelpers:

    def __init__(self, data):
    
        self._data = data

    @property
    def venue(self):
        return self._data.get('venue')

    @property
    def city(self):
        return self._data.get('city')

    @property
    def state(self):
        return self._data.get('state')

    @property
    def country(self):
        return self._data.get('country')

    def load(self, args):

        if args.venue:
            self._data['venue'] = args.venue
        if args.city:
            self._data['city'] = args.city
        if args.state:
            self._data['state'] = args.state
        if args.country:
            self._data['country'] = args.country

        return self

    def __str__(self):

        # city      city, ST    city (CTY)  city, ST (CTY)
        # ST                    ST (CTY)
        # CTY

        _output = ''

        if self.venue:
            _output += f' at {self.venue}'

        if self.city and not self.state and not self.country:
            _output += f' in {self.city}'

        if self.city and self.state and not self.country:
            # for city + state will do city, sta.
            try:
                _state = us.states.lookup(self.state).ap_abbr
            except:
                _state = self.state
            _output += f' in {self.city}, {_state}'

        if self.city and self.state and self.country:
            # for city + state + country will do city, sta. (country)
            try:
                _state = us.states.lookup(self.state).ap_abbr
            except:
                _state = self.state
            _output += f' in {self.city}, {_state} ({self.country})'

        if self.city and not self.state and self.country:
            # for city + country will do city, cty
            _output += f' in {self.city}, {self.country}'

        if not self.city and self.state and not self.country:
            # for state only, will do sta.
            try:
                _state = us.states.lookup(self.state).ap_abbr
            except:
                _state = self.state
            _output += f' in {_state}'

        if not self.city and self.state and self.country:
            # for state country, will do sta., CTY
            try:
                _state = us.states.lookup(self.state).ap_abbr
            except:
                _state = self.state
            _output += f' in {_state}, {self.country}'

        if not self.city and not self.state and self.country:
            _output += f' in {self.country}'

        return _output
