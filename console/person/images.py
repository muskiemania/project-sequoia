import traceback
import requests

from helpers import image_helpers

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

        _key = args.img.upper()
        _key = _key + '_' + args.on.replace('-', '') if args.on else _key

        if _key not in self._data:
            self._data[_key] = {}

        self._data[_key]['src'] = args.src or self._data[_key]['src']
        self._data[_key]['on'] = args.on or 'unknown'

        if args.put:
            # first need to try to get the local file bytes
            print('PUT')
            print(args.put)
            try:
                with open(args.put, 'rb') as f:
                    object_key = f'{self.__person.id}_{_key}.png'
                    files = {'file': (object_key, f)}
                    presigned = self._image_helpers.create_presigned_post(object_key)
                    http_response = requests.post(presigned['url'], data=presigned['fields'], files=files)
                    print(http_response)
            except:
                print('could not upload file to remote storage')
                
                traceback.print_exc()

        return self._data

    def init(self, _config):

        if self._data is None:
            self._data = {}

        self._image_helpers = image_helpers.ImageHelpers().init(_config)

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

        for k in self._data.keys():
            if k in _keys or any([k.startswith(y) for y in _keys]):
                i = self._data.get(k)
                img = Image()
                img.src = i.get('src').format(id=_id, ver=k.replace(' ', '_'))
                img.on = i.get('on')
                img.ver = k.split('_')[0]
                img.short = shorts[k] if k in shorts else k.split('_')[0]
                _images.append(img)

        #for k in _keys:
        #    if k in self._data:
        #        i = self._data.get(k)
        #        img = Image()
        #        img.src = i.get('src').format(id=_id, ver=k.replace(' ', '_'))
        #        img.on = i.get('on')
        #        img.ver = k
        #        img.short = shorts[k] if k in shorts else k
        #        _images.append(img)

        for _i in _images:
            _i.short = 'GRADUATION' if _i.short.startswith('GRADUATION') else _i.short
            _i.short = 'MARRIAGE' if _i.short.startswith('MARRIAGE') else _i.short

        return _images
    
    @property
    def P1(self):
        return self._data.get('P1')

    def __dict__(self):
        return self._data

    def __bool__(self):
        return bool(self._data)
