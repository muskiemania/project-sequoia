import os
import traceback
import datetime
import string
import random
import shutil

import art
import fpdf
import requests
import justifytext
import roman

from . import image_helpers

class PDFHelpers:

    def __init__(self):
        self._pdf = fpdf.FPDF(format='Letter', unit='pt')
        self.__this_page = []
        self.__index = []
        self.__column_number = None
        self.__wrapper = None
        self.__first_chapter = False

        self.__index_start = 0

        self.__COLUMN_WIDTH_CHARS = 43
        self.__COLUMN_WIDTH_CHARS_IMAGE = 27
        self.__LINE_HEIGHT_PTS = 10.0
        self.__SINGLE_COLUMN_WIDTH_IN = 6.5
        self.__DUAL_COLUMN_WIDTH_IN = 3.0
        self.__GUTTER_X_IN = 4.0
        self.__GUTTER_WIDTH_IN = 0.5
        self.__FIRST_COLUMN_X_IN = 1.0
        self.__SECOND_COLUMN_X_IN = 4.5
        self.__TOP_PTS = 72
        self.__DEFAULT_FONT = 'Courier'

        self._config = None
        self._image_helpers = None

    def init(self, _config):
        self._pdf.set_auto_page_break(False)
        self._pdf.set_font(self.__DEFAULT_FONT, '', 8.0)
        
        self.__write_title_page()

        self.__first_chapter = True

        self._config = _config
        self._image_helpers = image_helpers.ImageHelpers().init(_config)

        print(self._image_helpers)

        return self

    def __page_number(self):
        return self._pdf.page_no() - 1

    def __index_page(self):
        return roman.toRoman(self._pdf.page_no() - self.__index_start).lower()
    
    def __write_gutter(self):
        self._pdf.set_xy(72 * self.__GUTTER_X_IN, 72)
        self._pdf.multi_cell(72 * self.__GUTTER_WIDTH_IN, self.__LINE_HEIGHT_PTS, '\n'.join(['|' for _ in range(64)]), 0, 'C')

    def __write_footer(self):
        self._pdf.set_xy(72, 52)
        self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, f'{self.__this_page[0]}...')
        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 52)
        self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, f'...{self.__this_page[-1]}', 0, 'R')
        self._pdf.set_xy(72, (10 * 72) + 20)
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, f'-- Page {self.__page_number()} --', 0, 'C')
 
    def write_chapter(self, chapter, people, _begin_chapter=True):

        if self.__first_chapter:
            self._pdf.add_page()
            self._pdf.set_xy(self.__TOP_PTS, self.__TOP_PTS)
            self.__column_number = 1
            self.__first_chapter = False

        for person in people:
            _synopsis = str(person)

            # must check size before writing...
            _chapter_title = art.text2art(chapter, 'ogre')

            _wrapped_extended = justifytext.justify(person.extended, self.__COLUMN_WIDTH_CHARS)
            _filled_extended = '\n'.join(_wrapped_extended)
            _wrapped_synopsis = justifytext.justify(_synopsis, self.__COLUMN_WIDTH_CHARS)
            _filled_synopsis = '\n'.join(_wrapped_synopsis)

            _lines_chapter_title = len(_chapter_title.split('\r\n')) if _begin_chapter else 0
            _lines_for_person = len(_wrapped_extended) + len(_wrapped_synopsis)

            #if len(person.images) > 1:
            #    _lines_for_person += 10
            if len(person.images) == 1:
                _wrapped_extended = justifytext.justify(person.extended, self.__COLUMN_WIDTH_CHARS_IMAGE)
                _wrapped_synopsis = justifytext.justify(_synopsis, self.__COLUMN_WIDTH_CHARS_IMAGE)
     
                if len(_wrapped_extended) + len(_wrapped_synopsis) < 10:
                    _lines_for_person = 9
                else:
                    _second_part = _wrapped_synopsis[(10 - len(_wrapped_extended)):]
                    _second_part = ' '.join(_second_part)
                    _wrapped_part = justifytext.justify(_second_part, self.__COLUMN_WIDTH_CHARS_IMAGE)
                    _lines_for_person = 10 + len(_wrapped_part)

            if self._pdf.get_y() > ((72 * self.__LINE_HEIGHT_PTS) - (self.__LINE_HEIGHT_PTS * (1 + _lines_chapter_title + 1 + _lines_for_person))):
                
                if self.__column_number == 1:
                    self.__write_gutter()
                    self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72)
                    self.__column_number = 2
                    print('***** SECOND COL *****')
                
                elif self.__column_number == 2:
                    self.__write_footer()
                    
                    self._pdf.add_page()
                    self.__this_page = []
                    self._pdf.set_xy(72, 72)
                    self.__column_number = 1
                    print('***** NEW   PAGE *****')
                    print('***** FIRST  COL *****')

            if _begin_chapter:
                self._pdf.set_xy(72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + (0 if self._pdf.get_y() == 72 else 10))
                self._pdf.set_font(self.__DEFAULT_FONT, 'B')
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, _chapter_title)
                self._pdf.set_font('')
                print(_chapter_title + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
            
            self._pdf.set_xy(72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)    
            self._pdf.set_font(self.__DEFAULT_FONT, 'B')
 
            if (person.images and len(person.images) > 1) or not person.images:
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, _filled_extended, 0, 'L')
                self._pdf.set_font('')

            if person.images and len(person.images) == 1:

                _x = (72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN) + (72 * (self.__DUAL_COLUMN_WIDTH_IN - 1))
                _y = self._pdf.get_y()
                
                try:
                    _url = self._image_helpers.get_presigned_url(person.images[0].src)
                    _r = requests.get(_url, stream=True)

                    if _r.status_code != 200:
                        raise Exception('not 200 from aws')

                    _dest = 'tmp/' + person.images[0].src

                    with open(_dest, 'wb') as f:
                        shutil.copyfileobj(_r.raw, f)

                    self._pdf.image(_dest, _x, _y, 72, 90, type='png')
                    self._pdf.set_xy(_x + 72, _y)
                    self._pdf.multi_cell(18, self.__LINE_HEIGHT_PTS, '\n'.join(list(person.images[0].on)[:7]))
                except:
                    traceback.print_exc()
                else:
                    os.remove(_dest)
                finally:
                    self._pdf.rect(_x, _y, 72, 90, 'D')

                self._pdf.set_xy(72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, _y)
                self._pdf.multi_cell(72 * (self.__DUAL_COLUMN_WIDTH_IN - 1), self.__LINE_HEIGHT_PTS, _filled_extended, 0, 'L')
                self._pdf.set_font('')
                self._pdf.set_xy(72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())

                _first_part = _wrapped_synopsis[:(10 - len(_wrapped_extended))]
                self._pdf.multi_cell(72 * (self.__DUAL_COLUMN_WIDTH_IN - 1), self.__LINE_HEIGHT_PTS, '\n'.join(_first_part), 0, 'L')
                _filled_synopsis = _wrapped_synopsis[(10 - len(_wrapped_extended)):]
               
                # must unjustify these lines then re-wrap them
                for i, each in enumerate(_filled_synopsis):
                    _filled_synopsis[i] = ' '.join(each.split())

                _filled_synopsis = justifytext.justify(' '.join(_filled_synopsis), self.__COLUMN_WIDTH_CHARS)

                if len(_filled_synopsis) == 0:
                    _filled_synopsis = [' ' for i in range(9 - (len(_wrapped_extended) + len(_first_part)))]
            
                _filled_synopsis = '\n'.join(_filled_synopsis)

            self._pdf.set_xy(72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, _filled_synopsis, 0, 'L')
            
            self.__this_page.append(person.summary.split(',')[0])
            print(_filled_synopsis + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
            self.__index.append((person.summary, self.__page_number()))
            _begin_chapter = False

    def complete(self):
        if self.__this_page:
            self._pdf.set_xy(72, 52)
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'{self.__this_page[0]}...')
            self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 52)
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'...{self.__this_page[-1]}', 0, 'R')
            self._pdf.set_xy(72, (10 * 72) + 20)
            self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, f'-- Page {self.__page_number()} --', 0, 'C')
 
        self.__write_index()

        while self._pdf.page_no() % 4 > 0:
            self._pdf.add_page()

        _prefix = self._config['AWS.S3']['prefix']

        self._pdf.output(f'{_prefix}.pdf', 'F')

    def __write_index(self):

        self.__index_start = self._pdf.page_no()
        self._pdf.add_page()

        self._pdf.set_xy(72, 72)
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art('index', font='ogre'))
        self._pdf.set_font('')
        _column_number = 1
        _current_letter = ''

        for (summary, page_num) in self.__index:
            if summary[0].upper() != _current_letter:
                _current_letter = summary[0].upper()
                # check if room for 1 + subheader + 1 + name
                if self._pdf.get_y() > ((72 * 10) - (10 * (1 + 1 + 1 + 1))):
                    print('new section overflows')
                
                    if _column_number == 1:
                        self._pdf.set_xy(self.__GUTTER_X_IN * 72, 72)
                        self._pdf.multi_cell(72 * self.__GUTTER_WIDTH_IN, 10.0, '\n'.join(['|' for _ in range(64)]), 0, 'C')
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72)
                        _column_number = 2
                        print('***** SECOND COL *****')

                    elif _column_number == 2:
                        self._pdf.set_xy(72, (10 * 72) + 20)
                        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, f'-- {self.__index_page()} --', 0, 'C')
                    
                        self._pdf.add_page()
                        self._pdf.set_xy(72, 72)
                        _column_number = 1
                        print('***** NEW   PAGE *****')
                        print('***** FIRST  COL *****')

                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + (0 if self._pdf.get_y() == 72 else 10))
                
                self._pdf.set_font(self.__DEFAULT_FONT, 'B')
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'[{_current_letter.upper()}]')
                self._pdf.set_font('')

                print(_current_letter + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)
                
                _indexed_summary = summary + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + 2 + len(str(page_num)) + len(summary)))) + ('  ' + str(page_num))

                if len(summary) > 37:
                    # if the summary line is wider than the column, 
                    # then need to split the summary at the appropriate place 
                    # and then put the dots and page number on the next line
                    _split = _indexed_summary.find(' ', 30)
                    
                    if _split == -1 and len(summary) <= self.__COLUMN_WIDTH_CHARS:
                        _line_1 = summary
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + len(str(page_num))))) + ('  ' + str(page_num))
                    elif summary[_split:].strip() == '':
                        _line_1 = summary[:_split]
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + len(str(page_num))))) + ('  ' + str(page_num))
                    else:
                        _line_1 = summary[:_split]
                        _line_2 = summary[_split:]
                        _line_2 = '   ' + _line_2 + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (3 + 2 + 2 + len(_line_2) + len(str(page_num))))) + ('  ' + str(page_num))
                    
                    _indexed_summary = '\n'.join([_line_1, _line_2])

                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _indexed_summary)
                print(summary + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')

            elif summary[0].upper() == _current_letter:
                # check if room for name
                if self._pdf.get_y() > ((72 * 10) - 10):
                    print('name overflows')
                
                    if _column_number == 1:
                        self._pdf.set_xy(self.__GUTTER_X_IN * 72, 72)
                        self._pdf.multi_cell(72 * self.__GUTTER_WIDTH_IN, 10.0, '\n'.join(['|' for _ in range(64)]), 0, 'C')
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72)
                        _column_number = 2
                        print('***** SECOND COL *****')

                    elif _column_number == 2:
                        self._pdf.set_xy(72, (10 * 72) + 20)
                        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, f'-- {self.__index_page()} --', 0, 'C')
                    
                        self._pdf.add_page()
                        self._pdf.set_xy(72, 72)
                        _column_number = 1
                        print('***** NEW   PAGE *****')
                        print('***** FIRST  COL *****')

                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
                
                _indexed_summary = summary + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + 2 + len(str(page_num)) + len(summary)))) + ('  ' + str(page_num))
 
                if len(summary) > 37:
                    # if the summary line is wider than the column, 
                    # then need to split the summary at the appropriate place 
                    # and then put the dots and page number on the next line
                    _split = _indexed_summary.find(' ', 30)
                    
                    if _split == -1 and len(summary) <= self.__COLUMN_WIDTH_CHARS:
                        _line_1 = summary
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + len(str(page_num))))) + ('  ' + str(page_num))
                    elif summary[_split:].strip() == '':
                        _line_1 = summary[:_split]
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + len(str(page_num))))) + ('  ' + str(page_num))
                    else:
                        _line_1 = summary[:_split]
                        _line_2 = summary[_split:].split('.')[0].strip()
                        _line_2 = '   ' + _line_2 + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (3 + 2 + 2 + len(_line_2) + len(str(page_num))))) + ('  ' + str(page_num))
                    
                    _indexed_summary = '\n'.join([_line_1, _line_2])

                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _indexed_summary)
                print(summary + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')

        self._pdf.set_xy(72, (10 * 72) + 20)
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, f'-- {self.__index_page()} --', 0, 'C')
 
    def __write_title_page(self, prepared_for='muskiemania'):
        self._pdf.add_page()

        self._pdf.set_xy(72, 72)
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art('project', font='georgia11'))

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 30.0, art.text2art(' ', font='sequoia'), 0, 'C')

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art('   sequoia', font='georgia11'), 0, 'R')

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art(f' ', font='mini'), 0, 'C')
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art(f'prepared for:', font='mini'), 0, 'C')
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art(f'{prepared_for}', font='mini'), 0, 'C')
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art(f'on {datetime.datetime.now().strftime("%B %d, %Y")}', font='mini'), 0, 'C')
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art(f' ', font='mini'), 0, 'C')
 
        _tree = """
        MMMMMMMMMMNOdxk0WMMMMMMMMMMM
        MMMMMMMMWKdlllloxKWMMMMMMMMM
        MMMMMMMNkollllllloONMMMMMMMM
        MMMMMWKxolllllllllld0WMMMMMM
        MMMMW0dooooolooooooookXMMMMM
        MMMNOoooooooooooooooooxXMMMM
        MMMWKOOxolooooooooodO0XWMMMM
        MMMMMWKdlllllllooood0WMMMMMM
        MMMMNOololllllllllllokXMMMMM
        MMMXxolllollllllllloood0NMMM
        MMKdllllllllllllllloolloONMM
        MMX0Okolllllllllllllld0XNWMM
        MMMMNkollllllllllllllokXMMMM
        MMWKxooooooooooooooooold0NMM
        MNOdoooooooooooooooooooooxKW
        NkdoooooooooooooooooooooooxX
        NOkkxxxxxddddooddxxkkkOO00XW
        MMWWWWNNNNNKxooxKNWWWMMMMMMM
        MMMMMMMMMMMKdoodKMMMMMMMMMMM
        MMMMMMMMMMMXkxxkKMMMMMMMMMMM
        """
        _three_trees = _tree.split('\n')
        _three_trees = [t.strip().replace('M', ' ') for t in _three_trees]
        _three_trees = '\n'.join([t + '     ' + t + '     ' + t for t in _three_trees])
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, _three_trees, 0,'C')


