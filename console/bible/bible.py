from person import person

class Bible:

    def __init__(self, index={}):
        self._index = index

    def get_index(self):
        
        # index is a la the index in the back of a book...
        # so every person _id and their summary
        # sorted by summary text
        _index = []
        for (_, chapter) in self._index.items():
            for (_id, _person) in chapter.items():
                _index.append((_id, person.Person(_person, None).summary))

        return dict(_index)

    def get_toc(self):
        
        return list(self._index.keys())

    def get_chapter(self, page):

        if page not in self._index:
            return IndexError('key {page} not found in index')

        return self._index[page]

    def set(self, page, _id, section, _value):
        self._index[page][_id][section] = _value

    def add_person(self, person):
        
        _ix = dict(person)['_ix']
        _id = dict(person)['_id']

        if _ix not in self._index:
            self._index[_ix] = {}

        self._index[_ix][_id] = dict(person)

    def serialize(self, serializer):

        serializer.serialize(self)
        return True

    @staticmethod
    def deserialize(deserializer):

        _bible = Bible()
        _bible._index = deserializer.deserialize()
        return _bible
