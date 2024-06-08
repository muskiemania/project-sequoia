import traceback

class Images:

    def __init__(self, person):
    
        try:
            self.__person = person
            self._data = dict(person).get('images')

        except:
            traceback.print_exc()

    def load(self, args):

        if not args.img and not args.src:
            raise ValueError('missing required \'img\' and \'src\'')

        if self._data is None:
            self._data = {}

        if args.img.upper() not in self._data:
            self._data[args.img.upper()] = {}

        self._data[args.img.upper()]['src'] = args.src or self._data[args.img.upper()]['src']
        self._data[args.img.upper()]['on'] = args.on or 'unknown'

        return self._data

    def init(self):

        if self._data is None:
            self._data = {}

        return self

    def all(self, _id):
        Image = type('Image', (object,), {
            'src': '',
            'on': '',
            'ver': '',
            'short': ''
        })

        _images = []

        #if self.P1:
        #    p1 = Image()
        #    p1.src = self.P1.get('src').format(id=_id, ver='P1')
        #    p1.on = self.P1.get('on')
        #    _images.append(p1)

        #return _images

        _keys = ['P1', 'BAPTISM', 'FIRST EUCHARIST', 'CONFIRMATION', 'MARRIAGE', 'GRADUATION', 'RETIREMENT']

        #Image = type('Image', (object,), {
        #    'src': '',
        #    'on': '',
        #    'event': ''
        #})

        shorts = {
                'FIRST EUCHARIST': 'EUCHARIST'
                }

        for k in _keys:
            if k in self._data:
                i = self._data.get(k)
                img = Image()
                img.src = i.get('src').format(id=_id, ver=k.replace(' ', '_'))
                img.on = i.get('on')
                img.ver = k
                img.short = shorts[k] if k in shorts else k
                _images.append(img)

        return _images
    
    @property
    def P1(self):
        return self._data.get('P1')

    def __dict__(self):
        return self._data

    def __bool__(self):
        return bool(self._data)
