


class TabHelpers:

    def __init__(self, toc=None):

        self._toc = sorted(toc)
        self.index = True
        self.appendix = ['a', 'b', 'c', 'd']

    def generate(self, section, start='', end=''):

        _a_to_z = [f'/ {letter.upper()} /' for letter in  self._toc]
        _a_to_z = [('-----', l) for l in _a_to_z]

        _tabs = [('-----', letter.upper(), f'/ {letter.upper()} /', '-----') for letter in self._toc]
        if section == 'A' and start and end:
            for (i, (a, b, c, d)) in enumerate(_tabs):
                if start <= b <= end:
                    _tabs[i] = (a.replace('-', '*'), b, c.replace('/', '*'), d.replace('-', '*'))

        _index = ['-----']
        _index.extend([f'/ {letter.upper()} /' for letter in 'INDEX'])
        _index.extend(['-----'])
        _index = map(lambda x: x.replace('/', '*') if section == 'I' else x, _index)
        _index = map(lambda x: x.replace('-', '*') if section == 'I' else x, _index)

        _appendix = ['-----']
        _appendix.extend([f'/ {letter.upper()} /' for letter in 'APPENDIX'])
        _appendix.extend(['-----'])
        _appendix = map(lambda x: x.replace('/', '*') if section in 'X' else x, _appendix)
        _appendix = map(lambda x: x.replace('-', '*') if section in 'X' else x, _appendix)

        _appendixes = [('-----', letter.upper(), f'/ {letter.upper()} /', '-----') for letter in 'ABCD']
        if section in 'X' and start:
            for (i, (a, b, c, d)) in enumerate(_appendixes):
                if start == b:
                    _appendixes[i] = (a.replace('-', '*'), b, c.replace('/', '*'), d.replace('-', '*'))

        _output = []

        for (a, b, c, d) in _tabs:
            _output.append(a)
            _output.append(c)
            _output.append(d)
        
        _output.extend(_index)
        _output.extend(_appendix)

        for (a, b, c, d) in _appendixes:
            _output.append(a)
            _output.append(c)
            _output.append(d)

        _deduped = [v for i, v in enumerate(_output) if i == 0 or v != _output[i-1] or 'P' in v]
        _joined = '\n'.join(_deduped)
        _joined = _joined.replace('-----\n*****', '*****')
        _joined = _joined.replace('*****\n-----', '*****')


        return _joined

    def display(self, content):

        mode = 'R'
        search = '*'
        
        while content:

            if content.find(search) <= 0:
                _start = content.find(search)
                print(_start)
                print(mode)
                
                if _start < 0:
                    print(content)
                    break

                print(content[:_start])

                mode = 'B' if mode == 'R' else ('R' if mode == 'B' else mode)
                search = '/' if mode == 'B' else ('*' if mode == 'R' else search)
                content = content[_start:]





