from datetime import datetime, date, time

class Person(object):

    def __init__(self):
        self.data = {}
        
        name = {}
        name['last'] = ''
        name['first'] = ''
        name['middle'] = None
        name['initial'] = None
        name['suffix'] = None

        self.data['name'] = name
        
        self.data['sex'] = None
        
        birth = {}
        birth['year'] = None
        birth['month'] = None
        birth['date'] = None
        
        self.data['birthDate'] = birth

        death = {}
        death['year'] = None
        death['month'] = None
        death['date'] = None

        if death['year']:
            self.data['deathDate'] = death
        else:
            self.data['deathData'] = None

        self.info = []

    @staticmethod
    def Generate(obj):
        #input object must conform to underlying data structure
        p = Person()

        if 'name' in obj.keys():
            name = obj['name']
        
            if 'last' in name.keys():
                p._lastName = name['last']
            if 'first' in name.keys():
                p._firstName = name['first']
            if 'middle' in name.keys():
                p._middleName = name['middle']
            if 'initial' in name.keys():
                p._initial = name['initial']
            if 'suffix' in name.keys():
                p._suffix = name['suffix']

        if 'sex' in obj.keys():
            p._sex = obj['sex']

        if 'birthDate' in obj.keys():
            birthDate = obj['birthDate']
            (y,m,d) = p._extractDate(birthDate)
            p._birthDate = (y,m,d)

        if 'deathDate' in obj.keys():
            deathDate = obj['deathDate']
            (y,m,d) = p._extractDate(deathDate)
            p._deathDate = (y,m,d)

        return p

    @property
    def firstName(self):
        return self.data['name']['first']

    @firstName.setter
    def _firstName(self, value):
        self.data['name']['first'] = value

    @property
    def lastName(self):
        return self.data['name']['last']

    @lastName.setter
    def _lastName(self, value):
        self.data['name']['last'] = value

    @property
    def middleName(self):
        return self.data['name']['middle']

    @middleName.setter
    def _middleName(self, value):
        self.data['name']['middle'] = value

    @property
    def initial(self):
        return self.data['name']['initial']

    @initial.setter
    def _initial(self, value):
        self.data['name']['initial'] = value

    @property
    def suffix(self):
        return self.data['name']['suffix']

    @suffix.setter
    def _suffix(self, value):
        self.data['name']['suffix'] = value

    @property
    def sex(self):
        return self.data['sex']

    @sex.setter
    def _sex(self, value):
        self.data['sex'] = value

    @property
    def birthDate(self):
        obj = self.data['birthDate']
        return self._extractDate(obj)

    @birthDate.setter
    def _birthDate(self, (y,m,d)):
        self.data['birthDate']['year'] = y
        self.data['birthDate']['month'] = m
        self.data['birthDate']['date'] = d

    @property
    def deathDate(self):
        obj = self.data['deathDate']
        if obj == None:
            return None
        return self._extractDate(obj)

    @deathDate.setter
    def _deathDate(self, (y,m,d)):
        self.data['deathDate']['year'] = y
        self.data['deathDate']['month'] = m
        self.data['deathDate']['date'] = d

    @property
    def id(self):
        (y,m,d) = self.birthDate
        id = '_'.join([self.lastName[:7],self.firstName[:4],date(y,m,d).strftime("%b%d%Y")])
        return id.upper()

    def _extractDate(self, obj):
        return (obj['year'], obj['month'], obj['date'])
