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
            'on': ''
        })

        _images = []

        if self.P1:
            p1 = Image()
            p1.src = self.P1.get('src').format(id=_id, ver='P1')
            p1.on = self.P1.get('on')
            _images.append(p1)

        return _images
    
    @property
    def P1(self):
        return self._data.get('P1')

    def __dict__(self):
        return self._data

    def __bool__(self):
        return bool(self._data)
