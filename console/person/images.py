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

        self._data[args.img.upper()] = args.src or self._data.get(args.img.upper())

        return self._data

    def init(self):

        if self._data is None:
            self._data = {}

        return self

    def all(self):
        return [self.P1] if self.P1 else []
    
    @property
    def P1(self):
        return self._data.get('P1')

    def __dict__(self):
        return self._data

    def __bool__(self):
        return bool(self._data)
