import os
import argparse
import string

from bible import bible, serializer_factory, s3_serializer, local_serializer
from person import person, born, basic
from helpers import config_helpers

from tabulate import tabulate

if __name__ == '__main__':

    _parser = argparse.ArgumentParser()
    _parser.version = '1.0'
    _parser.add_argument('-R', 
        action='store', 
        type=str, 
        choices=['s3', 'local'],
        default='local',
        required=False,
        help='sets the datasource to read from'
    )
    _parser.add_argument('-C', 
        action='store_true', 
        required=False,
        help='creates new person (given, middle, surname, sex)'
    )
    _parser.add_argument('-E', 
        action='store',
        type=str, 
        choices=list(string.ascii_lowercase),
        required=False,
        help='sets the edit mode'
    )
    _parser.add_argument('-id', 
        action='store', 
        nargs='?',
        type=str,
        required=False,
        help='sets id of person'
    )
    _parser.add_argument('-basic', 
        action='store_true', 
        required=False,
        help='sets basic info for person (given, middle, surname, sex)'
    )
    _parser.add_argument('-given', 
        action='store',
        nargs='?',
        type=str,
        required=False,
        help='sets given name for person'
    )
    _parser.add_argument('-middle', 
        action='store',
        nargs='?',
        type=str,
        required=False,
        help='sets middle name for person'
    )
    _parser.add_argument('-surname', 
        action='store',
        nargs='?',
        type=str,
        required=False,
        help='sets surname for person'
    )
    _parser.add_argument('-sex', 
        action='store',
        nargs='?',
        type=str.lower,
        choices=['m', 'male', 'f', 'female'],
        required=False,
        help='sets sex for person'
    )
    _parser.add_argument('-born', 
        action='store_true', 
        required=False,
        help='sets birth data for person'
    )
    _parser.add_argument('-on', 
        action='store',
        nargs='?',
        type=str,
        required=False,
        help='sets date for event'
    )
    _parser.add_argument('-city', 
        action='store',
        nargs='?',
        type=str,
        required=False,
        help='sets city for event location'
    )
    _parser.add_argument('-state', 
        action='store',
        nargs='?',
        type=str,
        required=False,
        help='sets state for event location'
    )
    _parser.add_argument('-country', 
        action='store',
        nargs='?',
        type=str,
        required=False,
        help='sets country for event location'
    )
    
    _parser.add_argument('-parents', 
        action='store',
        nargs='+',
        type=str,
        required=False,
        help='sets birth parents'
    )

    _parser.add_argument('-T', 
        action='store', 
        type=str, 
        choices=list(string.ascii_lowercase),
        required=False,
        help='gets TOC for a single page'
    )
    _parser.add_argument('-O', 
        action='store', 
        type=str, 
        choices=list(string.ascii_lowercase),
        required=False,
        help='gets textualized output for a single page'
    )
    _parser.add_argument('-W', 
        action='store', 
        type=str, 
        choices=['s3', 'local'],
        default='local',
        required=False,
        help='sets the datasource to write to'
    )

    _args = _parser.parse_args()

    _path_dir = os.path.dirname(__file__)
    _path_file = os.path.join(_path_dir, '.sequoia')
    _config = config_helpers.ConfigHelpers(_path_file).init().get_config()
    _bible = None

    # first must read no matter what
    if _args.R:
        _serializer = serializer_factory.SerializerFactory.generate(_args.R, _config)
        _bible = bible.Bible.deserialize(_serializer)

        _index = _bible.get_index()
    if _args.C:
        _given = _args.given
        _middle = _args.middle
        _surname = _args.surname
        _sex = _args.sex
        _born = _args.on

        _new_person = person.Person.create(_given, _middle, _surname, _sex, _born)
        _bible.add_person(_new_person)

    if _args.E:
        _page = _bible.get_chapter(_args.E.lower())
        _id = _args.id

        if _id not in _page:
            raise KeyError(f'id {_id} not found in page \'{_args.E.lower()}\'')
        _person = person.Person(_page[_id], _index)
        if _args.basic:
            _basic = basic.Basic(_person).load(_args)
            _bible.set(_args.E.lower(), _id, 'basic', _basic)
        if _args.born:
            _born = born.Born(_person).load(_args)
            _bible.set(_args.E.lower(), _id, 'born', _born)

    if _args.O:
        _page = _bible.get_chapter(_args.O.lower())
        _persons = sorted([person.Person(v, _index).init() for (k,v) in _page.items()], key=lambda x: x.sort_key)

        print('\n'.join([str(person) for person in _persons]))

    if _args.T:
        _page = _bible.get_chapter(_args.T.lower())
        _headers = ['given', 'm.i.', 'surname', 'd.o.b.', 'sex', '_id']
        _persons = sorted([person.Person(v, _index).init() for (k,v) in _page.items()], key=lambda x: x.sort_key)
        _data = [[dict(person)['basic']['given'], dict(person)['basic']['middle'][0] if dict(person)['basic']['middle'] else '?', dict(person)['basic']['surname'], dict(person)['born']['on'], dict(person)['basic']['sex'], dict(person)['_id']] for person in _persons]
        print(tabulate(_data, headers=_headers))

    # write must be left until last...but not always required
    if not _args.O and not _args.T and _args.W:

        _serializer = serializer_factory.SerializerFactory.generate(_args.W, _config)
        _bible.serialize(_serializer)

    #me = person.Person.create('justin', 'muskivitch', '1982-02-16', 'm')

    #_bible = bible.Bible()

    #_path_dir = os.path.dirname(__file__)
    #_path_file = os.path.join(_path_dir, '.sequoia')
    #_config = config_helpers.ConfigHelpers(_path_file).init().get_config()

    #_serializer = serializer.BibleSerializer(_config)

    #_bible.add_person(me)

    #_bible.serialize(_serializer)
