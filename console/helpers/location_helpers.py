import traceback

class LocationHelpers:

    def __init__(self, data):
    
        self._data = data

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

        if self.city and not self.state and not self.country:
            _output += f' in {self.city}'

        if self.city and self.state and not self.country:
            _output += f' in {self.city}, {self.state}'

        if self.city and self.state and self.country:
            _output += f' in {self.city}, {self.state} ({self.country})'

        if self.city and not self.state and self.country:
            _output += f' in {self.city} ({self.country})'

        if not self.city and self.state and not self.country:
            _output += f' in {self.state}'

        if not self.city and self.state and self.country:
            _output += f' in {self.state} ({self.country})'

        if not self.city and not self.state and self.country:
            _output += f' in {self.country}'

        return _output
