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

def __setupDeadFemale():
    obj = {}
    name = {}
    name['first'] = 'GirlName'
    name['last'] = 'LastName'
    name['middle'] = 'GirlMiddle'
    name['initial'] = 'G'

    obj['name'] = name

    obj['sex'] = 'F'

    birth = {}
    birth['year'] = 1911
    birth['month'] = 2
    birth['date'] = 3

    obj['birthDate'] = birth

    death = {}
    death['year'] = 1999
    death['month'] = 12
    death['date'] = 31

    obj['deathDate'] = death

    return obj

def test_FirstName():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)

    assert (p.firstName, f.firstName) == ('FirstName', 'GirlName')

def test_LastName():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    assert (p.lastName, f.lastName) == ('LastName','LastName')

def test_MiddleName():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    assert (p.middleName, f.middleName) == ('MiddleName','GirlMiddle')

def test_Initial():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    assert (p.initial, f.initial) == ('I', 'G')

def test_Suffix():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    assert p.suffix == 'III'
    assert f.suffix == None

def test_Sex():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    assert p.sex == 'M'
    assert f.sex == 'F'

def test_BirthDate():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    assert p.birthDate == (2010, 1, 2)
    assert f.birthDate == (1911, 2, 3)

def test_DeathDate():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    assert p.deathDate == None
    assert f.deathDate == (1999, 12, 31)

def test_PersonID():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    assert p.id == 'LASTNAM_FIRS_JAN022010'
    assert f.id == 'LASTNAM_GIRL_FEB031911'

def test_GetHeadline():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    
    assert p.GetHeadline() == "LastName, F M (****-)"
    assert p.GetHeadline(redacted = True) == "LastName, F M (****-)"
    assert p.GetHeadline(redacted = False) == "LastName III, FirstName MiddleName (2010-)"

    assert f.GetHeadline() == "LastName, GirlName GirlMiddle (1911-1999)"
    assert f.GetHeadline(redacted = True) == "LastName, G G (****-****)"
    assert f.GetHeadline(redacted = False) == "LastName, GirlName GirlMiddle (1911-1999)"

def test_GetName():
    male = __setupLivingMale()
    female = __setupDeadFemale()
    p = Person.Generate(male)
    f = Person.Generate(female)
    
    assert p.GetName() == "F M LastName (****-)"
    assert p.GetName(redacted = True) == "F M LastName (****-)"
    assert p.GetName(redacted = False) == "FirstName MiddleName LastName, III (2010-)"

    assert f.GetName() == "GirlName GirlMiddle LastName (1911-1999)"
    assert f.GetName(redacted = True) == "G G LastName (****-****)"
    assert f.GetName(redacted = False) == "GirlName GirlMiddle LastName (1911-1999)"

