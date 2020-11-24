

class Bible:

    def __init__(self, index={}):
        self._index = index

    def get_index(self):
        return list(self._index.keys())

    def get_persons(self, page):

        if page not in self._index:
            return IndexError('key {page} not found in index')

        return self._index[page]

    def set(self, page, _id, section, _value):
        self._index[page][_id][section] = _value

    def add_person(self, person):
        
        _ix = person['_ix']
        _id = person['_id']

        if _ix not in self._index:
            self._index[_ix] = {}

        self._index[_ix][_id] = person

    def serialize(self, serializer):

        serializer.serialize(self)
        return True

    @staticmethod
    def deserialize(deserializer):

        _bible = Bible()
        _bible._index = deserializer.deserialize()
        return _bible
