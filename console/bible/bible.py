

class Bible:

    def __init__(self):
        self._index = {}

    def get_index(self):
        return list(self._index.keys())

    def get_persons(self, page):

        if page not in self._index:
            return IndexError('key {page} not found in index')

        return self._index[page]

    def add_person(self, person):
        
        _ix = person['_ix']
        _id = person['_id']

        if _ix not in self._index:
            self._index[_ix] = {}

        self._index[_ix][_id] = person

    def serialize(self, serializer):

        serializer.serialize(self)
