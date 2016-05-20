from person import Person

def __setupLivingMale():
    obj = {}
    name = {}
    name['first'] = 'FirstName'
    name['last'] = 'LastName'
    name['middle'] = 'MiddleName'
    name['initial'] = 'I'
    name['suffix'] = 'III'

    obj['name'] = name

    obj['sex'] = 'M'

    birth = {}
    birth['year'] = 2010
    birth['month'] = 1
    birth['date'] = 2

    obj['birthDate'] = birth

    return obj

def test_FirstName():
    obj = __setupLivingMale()
    p = Person.Generate(obj)
    assert p.firstName == 'FirstName'

def test_LastName():
    obj = __setupLivingMale()
    p = Person.Generate(obj)
    assert p.lastName == 'LastName'

def test_MiddleName():
    obj = __setupLivingMale()
    p = Person.Generate(obj)
    print p
    assert p.middleName == 'MiddleName'

def test_Initial():
    obj = __setupLivingMale()
    p = Person.Generate(obj)
    print p
    assert p.initial == 'I'

def test_Suffix():
    obj = __setupLivingMale()
    p = Person.Generate(obj)
    print p
    assert p.suffix == 'III'

def test_Sex():
    obj = __setupLivingMale()
    p = Person.Generate(obj)
    print p
    assert p.sex == 'M'

def test_BirthDate():
    obj = __setupLivingMale()
    p = Person.Generate(obj)
    assert p.birthDate == (2010, 1, 2)

def test_PersonID():
    obj = __setupLivingMale()
    p = Person.Generate(obj)
    assert p.id == 'LASTNAM_FIRS_JAN022010'
