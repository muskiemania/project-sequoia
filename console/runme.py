import os
import argparse
import string

from bible import bible, serializer_factory, s3_serializer, local_serializer
from person import person
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
        _bible = _serializer.deserialize()

    if _args.O:
        _page = _bible[_args.O.lower()]

        print('\n'.join([str(person.Person(v)) for (k,v) in _page.items()]))

    if _args.T:
        _page = _bible[_args.T.lower()]
        _headers = ['given', 'm.i.', 'surname', 'd.o.b.', 'sex', '_id']
        _data = [[person['givenName'], '?', person['surname'], person['born'], person['sex'], person['_id']] for person in _page.values()]
        print(tabulate(_data, headers=_headers))

    # write must be left until last...but not always required
    if not _args.O and not _args.T and _args.W:
        _serializer = serializer_factory.SerializerFactory.generate(_args.W, _config)
        _serializer.serialize(_bible)

    #me = person.Person.create('justin', 'muskivitch', '1982-02-16', 'm')

    #_bible = bible.Bible()

    #_path_dir = os.path.dirname(__file__)
    #_path_file = os.path.join(_path_dir, '.sequoia')
    #_config = config_helpers.ConfigHelpers(_path_file).init().get_config()

    #_serializer = serializer.BibleSerializer(_config)

    #_bible.add_person(me)

    #_bible.serialize(_serializer)
