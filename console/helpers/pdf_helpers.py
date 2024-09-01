import os
import traceback
import datetime
import string
import random
import shutil
import math

import art
import fpdf
import requests
import justifytext
import roman

from . import image_helpers
from . import tab_helpers

class PDFHelpers:

    def __init__(self):
        self._pdf = fpdf.FPDF(format='Letter', unit='pt')
        self.__this_page = []
        self.__index = []
        self.__appendix_a = []
        self.__appendix_b = []
        self.__appendix_c = []
        self.__appendix_d = []
        self.__appendix_e = []
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
        self.toc = []

    def init(self, _config):
        self._pdf.set_auto_page_break(False)
        self._pdf.set_font(self.__DEFAULT_FONT, '', 8.0)
        
        self.__write_title_page()

        self.__first_chapter = True

        self._config = _config
        self._image_helpers = image_helpers.ImageHelpers().init(_config)

        #print(self._image_helpers)

        return self

    @property
    def __page_number(self):
        return self._pdf.page_no() - 1

    @property
    def __index_page(self):
        return roman.toRoman(self._pdf.page_no() - self.__index_start).lower()
    
    def __write_gutter(self, start_line = 1):
        self._pdf.set_xy(72 * self.__GUTTER_X_IN, 72 + ((start_line - 1) * 10))
        self._pdf.multi_cell(72 * self.__GUTTER_WIDTH_IN, self.__LINE_HEIGHT_PTS, '\n'.join(['|' for _ in range(64 - (start_line - 1))]), 0, 'C')

    def __write_footer(self, page_number, section='A', sub=''):
        
        # this is not the footer, but cannot write the header when start of page is writteen because do not know how much content is written (shrug)
        _first_name_on_page = ' '
        _last_name_on_page = ' '

        if self.__this_page:
            _first_name_on_page = self.__this_page[0]
            _last_name_on_page = self.__this_page[-1]
            self.__this_page = []
            self._pdf.set_xy(72, 52)
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, f'{_first_name_on_page}...')
            self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 52)
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, f'...{_last_name_on_page}', 0, 'R')
       
        _t = tab_helpers.TabHelpers(toc=self.toc)
        left = self.__page_number % 2 == 1
        _x = 24 if left else (72 + (72 * self.__SINGLE_COLUMN_WIDTH_IN) + 24)
        _y = 72

        _start_end = {
                'A': (_first_name_on_page[0], _last_name_on_page[0]),
                'I': (None, None),
                'X': (sub, None)
                }


        _tabs = _t.generate(section, start=_start_end[section][0], end=_start_end[section][1])

        def __render_tabs(self, content):
            nonlocal _x
            nonlocal _y
            mode = 'B' if content[0] == '*' else 'R'
            search = '*' if mode == 'R' else '/'

            while content:

                print(f'mode: {mode} search: {search} _start: {content.find(search)} length: {len(content)}')

                _start = content.find(search)
                self._pdf.set_xy(_x, _y)
                self._pdf.set_font(self.__DEFAULT_FONT, '' if mode == 'R' else 'B')
                if _start < 0:
                    self._pdf.multi_cell(72 * 0.5, self.__LINE_HEIGHT_PTS, content, 0, 'L')
                    break

                self._pdf.multi_cell(72 * 1, self.__LINE_HEIGHT_PTS, content[:_start], 0, 'L')
                _y += (self.__LINE_HEIGHT_PTS * (len(content[:_start].split('\n')) - 1))
                mode = 'B' if mode == 'R' else ('R' if mode == 'B' else mode)
                search = '/' if mode == 'B' else ('*' if mode == 'R' else search)
                content = content[_start:]
                
            self._pdf.set_font(self.__DEFAULT_FONT, '')
 

        __render_tabs(self, _tabs)

        # write page number at bottom
        self._pdf.set_xy(72, (10 * 72) + 20)
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, f'-- Page {page_number} --', 0, 'C')
 
    def write_chapter(self, chapter, people_tree, _begin_chapter=True):

        if self.__first_chapter:
            self._pdf.add_page()
            self._pdf.set_xy(self.__TOP_PTS, self.__TOP_PTS)
            self.__column_number = 1
            self.__first_chapter = False

        for (person, tree) in people_tree:
            _synopsis = str(person)

            # must check size before writing...
            _chapter_title = art.text2art(chapter, 'ogre')

            _wrapped_extended = justifytext.justify(person.extended, self.__COLUMN_WIDTH_CHARS)
            _filled_extended = '\n'.join(_wrapped_extended)
            _wrapped_synopsis = justifytext.justify(_synopsis, self.__COLUMN_WIDTH_CHARS)
            _filled_synopsis = '\n'.join(_wrapped_synopsis)

            _lines_chapter_title = len(_chapter_title.split('\n')) if _begin_chapter else 0
            _lines_for_person = len(_wrapped_extended) + len(_wrapped_synopsis)


            _images = [i for i in person.images if i.ver in ['P0', 'P1', 'P2']]
            if len(_images) == 1:
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
                    self.__write_footer(self.__page_number)
                    
                    self._pdf.add_page()
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

            _images = [i for i in person.images if i.ver in ['P0', 'P1', 'P2']]

            if (_images and len(_images) > 1) or not _images:
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, _filled_extended, 0, 'L')
                self._pdf.set_font('')

            if _images and len(_images) == 1:

                _x = (72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN) + (72 * (self.__DUAL_COLUMN_WIDTH_IN - 1))
                _y = self._pdf.get_y()
                
                try:
                    _url = self._image_helpers.get_presigned_url(_images[0].src)
                    _r = requests.get(_url, stream=True)

                    if _r.status_code != 200:
                        print(f'presigned url: {_url}')
                        raise Exception('not 200 from aws - ' + str(_r.content))

                    _dest = 'tmp/' + _images[0].src

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
            print(person.summary)
            print(_filled_synopsis + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
            self.__index.append((person.summary, self.__page_number, person.id))

            # generate appendix content
            self.__appendix_a.append((person.summary, person.appendix_a, person.images))
            self.__appendix_b.append((person.summary, person.appendix_b))
            
            person.tree = tree
            if person.appendix_c:
                self.__appendix_c.append((person.summary, self.__page_number, person.appendix_c))

            if person.appendix_d:
                self.__appendix_d.append(tuple(person.summary) + person.appendix_d)

            if person.appendix_e:
                self.__appendix_e.append((person.summary, person.appendix_e))

            _begin_chapter = False

    def complete(self):
        self.__write_footer(self.__page_number)
 
        self.__write_index()
        self.__write_appendix_a()
        self.__write_appendix_b()
        self.__write_appendix_c()
        self.__write_appendix_d()
        self.__write_appendix_e()

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

        for (summary, page_num, _) in self.__index:
            if summary[0].upper() != _current_letter:
                _current_letter = summary[0].upper()
                # check if room for 1 + subheader + 1 + name
                if self._pdf.get_y() > ((72 * 10) - (10 * (1 + 1 + 1 + 1))):
                    print('new section overflows')
                
                    if _column_number == 1:
                        self.__write_gutter()
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72)
                        _column_number = 2
                        print('***** SECOND COL *****')

                    elif _column_number == 2:
                        self.__write_footer(self.__index_page, section='I')
                    
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
                        self.__write_gutter()
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72)
                        _column_number = 2
                        print('***** SECOND COL *****')

                    elif _column_number == 2:
                        self.__write_footer(self.__index_page, section='I')
                    
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

        self.__write_footer(self.__index_page, section='I')

    def __write_appendix_a(self): # special occasions
        self._pdf.add_page()
        self.__appendix_a_start = self._pdf.page_no()

        self._pdf.set_xy(72, 72)
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art('appendix a', font='ogre'))
        self._pdf.set_font('')

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, '\n[CHRONOLOGY OF SPECIAL EVENTS]')
        self._pdf.set_font('')

        _column_number = 1
        _current_letter = ''

        def __first_page_of_appendix_a(self):
            return self._pdf.page_no() == self.__appendix_a_start

        def __draw_images(self):
            return

        def __next_column(self, column_number):
            if column_number == 1:
                self.__write_gutter(8 if __first_page_of_appendix_a(self) else 1)
                self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72 + ((6 if __first_page_of_appendix_a(self) else 0) * 10))
                # print NAME (continued...)

                print('***** SECOND COL *****')
                return 2

            elif column_number == 2:
                # add to _this_page
                self.__write_footer(self.__index_page, section='X', sub='A')
                    
                self._pdf.add_page()
                self._pdf.set_xy(72, 72)
    
                # print NAME (continued...)

                print('***** NEW   PAGE *****')
                print('***** FIRST  COL *****')
                return 1
        
        def __write_header(self, letter):
            self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + (0 if self._pdf.get_y() == 72 else 10))
            self._pdf.set_font(self.__DEFAULT_FONT, 'B')
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'[{letter.upper()}]')
            self._pdf.set_font('')

        def __write_summary(self, summary, continued=False):

            self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + (0 if continued else 10))
            #self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
            self._pdf.set_font(self.__DEFAULT_FONT, 'B')
            if continued:
                summary += '\n' + 'Continued...'
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'{summary}')
            self._pdf.set_font('')
 
        def __write_events(self, events):
            self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
               
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, '\n'.join(events))




        # FOR EACH PERSON
        for (_summary, events, images) in self.__appendix_a:
            print(f'{_summary}')

            _events = events.as_list

            if not _events:
                print(f'  - no events')
                continue

            if _summary[0].upper() != _current_letter:
                _current_letter = _summary[0].upper()

                images = sorted([i for i in images if i.ver not in ['P1']], key=lambda x: x.on)
 
                # SCENARIO A - the whole thing fits!
                _len_e = len(str(events).split('\n'))
                _len_i = (math.ceil(len(images)/3) * (11 - 1)) + ((math.ceil(len(images)/3)) - 1) * 3


                _A = self._pdf.get_y() + (10 * (1 + 1 + 1 + 1 + _len_e + _len_i)) <= (72 * self.__LINE_HEIGHT_PTS)
                # SCENARIO B - it doesnt fit - full push
                _B = not _A and (len(_events) == 1 and images)
                # SCENARIO C - it doesnt fit - split
                #_C = not _A and (len(_events) > 1)
                _C = False 
                # must check if exists any viable split that fits
                _i = len(_events) - 1

                print('first in section')
                print(f'A {_A} B {_B} C {_C}')
                print(f'y: {self._pdf.get_y()} len_e: {_len_e} len_i: {_len_i}')

                while not _A and _i >= 1:
                    _height = len('\n'.join(_events[:_i]).split('\n'))
                    _fits = self._pdf.get_y() + ((10 * (1 + 1 + 1 +_height))) <= (72 * self.__LINE_HEIGHT_PTS)
                    if _fits:
                        _C = True
                        break

                    _i = _i - 1


                if (_B and not _C) or not any([_A, _B, _C]):
                    print('scenario B')
                    print('new section overflows')
                    _column_number = __next_column(self, _column_number)
                    __write_header(self, _current_letter)
                    __write_summary(self, _summary)
                    __write_events(self, _events)
                    # write images
                elif _C:
                    print('scenario C')
                    __write_header(self, _current_letter)
                    __write_summary(self, _summary)
                    __write_events(self, _events[:_i])
                    print('section overflows')
                    _column_number = __next_column(self, _column_number)
                    __write_summary(self, _summary, True)
                    __write_events(self, _events[_i:])
                    # write images
                elif _A:
                    print('scenario A')
                    __write_header(self, _current_letter)
                    __write_summary(self, _summary)
                    __write_events(self, _events)
                    # write images
                         
                while images:
                    print(images)
                    # set position for first image
                    self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)

                    _x = (72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN)
                    _y = self._pdf.get_y()

                    _xy = {}
                    _xy['0'] = (_x - 5, _y + 10)
                    _xy['1'] = (_x + 72, _y + 10)
                    _xy['2'] = (_x + 72 + 5 + 72, _y + 10)

                    #  | --- 72 --- | --- 72 --- | --- 72 --- |
                    #| --- 72 --- |5| --- 72 --- |5| --- 72 --- |

                    #     /\      
                    #    /\*\     
                    #   /\O\*\    
                    #  /*/\/\/\   
                    # /\O\/\*\/\  
                    #     ||      
                    #     ||      
                    #     ||      
                    
                    _ascii_tree = '' + '\n'
                    _ascii_tree += '       /\\' + '\n'      
                    _ascii_tree += '      /\\*\\' + '\n'     
                    _ascii_tree += '     /\\O\\*\\' + '\n'    
                    _ascii_tree += '    /*/\\/\\/\\' + '\n'   
                    _ascii_tree += '   /\\O\\/\\*\\/\\' + '\n'
                    _ascii_tree += '       ||' + '\n'
                    _ascii_tree += '       ||'

                    for i, img in enumerate(images[:3]):
                        
                        (x, y) = _xy[str(i)]

                        try:
                            _url = self._image_helpers.get_presigned_url(img.src)
                            _r = requests.get(_url, stream=True)

                            if _r.status_code != 200:
                                print(f'presigned url: {_url}')
                                raise Exception('not 200 from aws - ' + str(_r.content))

                            _dest = 'tmp/' + img.src

                            with open(_dest, 'wb') as f:
                                shutil.copyfileobj(_r.raw, f)
                            self._pdf.image(_dest, x, y, 72, 90, type='png')
                        except:
                            traceback.print_exc()
                            self._pdf.set_xy(x - 5, y)
                            self._pdf.multi_cell(72, 10.0, _ascii_tree)
                        else:
                            os.remove(_dest)

                        finally:
                            self._pdf.set_font(self.__DEFAULT_FONT, 'B')
                            self._pdf.set_xy(x, y - self.__LINE_HEIGHT_PTS)
                            self._pdf.multi_cell(72, self.__LINE_HEIGHT_PTS, img.short)
                            self._pdf.set_xy(x, y + 90)
                            self._pdf.multi_cell(72, self.__LINE_HEIGHT_PTS, img.on[:10])
                            self._pdf.set_font('')
                            self._pdf.rect(x, y, 72, 90, 'D')

                    images = images[3:]
                    self._pdf.set_xy(_x, _y + 72 + (30 if images else 40))
                
                print(str(events) + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')


            elif _summary[0].upper() == _current_letter:
                
                images = sorted([i for i in images if i.ver not in ['P1']], key=lambda x: x.on)
 


                # SCENARIO A - the whole thing fits!
                _len_e = len(str(events).split('\n'))
                _len_i = (math.ceil(len(images)/3) * (11 - 1)) + ((math.ceil(len(images)/3)) - 1) * 3


                _A = self._pdf.get_y() + (10 * (1 + 1 + _len_e + _len_i)) <= (72 * self.__LINE_HEIGHT_PTS)
 
                # SCENARIO B - it doesnt fit - full push
                _B = not _A and (len(_events) == 1 and images)
                # SCENARIO C - it doesnt fit - split
                #_C = not _A and (len(_events) > 1)
                _C = False
                # must check if exists any viable split that fits
                _i = len(_events) - 1

                print(f'A {_A} B {_B} C {_C}')
                print(f'y: {self._pdf.get_y()} len_e: {_len_e} len_i: {_len_i}')

                while not _A and _i >= 1:
                    _height = len('\n'.join(_events[:_i]).split('\n'))
                    _fits = self._pdf.get_y() + ((10 * (1 +_height))) <= (72 * self.__LINE_HEIGHT_PTS)
                    if _fits:
                        _C = True
                        break

                    _i = _i - 1

                if (_B and not _C) or not any([_A, _B, _C]):
                    print('scenario B')
                    print('new section overflows')
                    _column_number = __next_column(self, _column_number)
                    __write_summary(self, _summary)
                    __write_events(self, _events)
                    # write images
                elif _C:
                    print('scenario C')
                    __write_summary(self, _summary)
                    __write_events(self, _events[:_i])
                    print('section overflows')
                    _column_number = __next_column(self, _column_number)
                    __write_summary(self, _summary, True)
                    __write_events(self, _events[_i:])
                    # write images
                elif _A:
                    print('scenario A')
                    __write_summary(self, _summary)
                    __write_events(self, _events)
                    # write images
 
                while images:
                    print(images)
                    # set position for first image
                    self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)

                    _x = (72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN)
                    _y = self._pdf.get_y()

                    _xy = {}
                    _xy['0'] = (_x - 5, _y + 10)
                    _xy['1'] = (_x + 72, _y + 10)
                    _xy['2'] = (_x + 72 + 5 + 72, _y + 10)

                    #  | --- 72 --- | --- 72 --- | --- 72 --- |
                    #| --- 72 --- |5| --- 72 --- |5| --- 72 --- |

                    #     /\      
                    #    /\*\     
                    #   /\O\*\    
                    #  /*/\/\/\   
                    # /\O\/\*\/\  
                    #     ||      
                    #     ||      
                    #     ||      
                    
                    _ascii_tree = '' + '\n'
                    _ascii_tree += '       /\\' + '\n'      
                    _ascii_tree += '      /\\*\\' + '\n'     
                    _ascii_tree += '     /\\O\\*\\' + '\n'    
                    _ascii_tree += '    /*/\\/\\/\\' + '\n'   
                    _ascii_tree += '   /\\O\\/\\*\\/\\' + '\n'
                    _ascii_tree += '       ||' + '\n'
                    _ascii_tree += '       ||'

                    for i, img in enumerate(images[:3]):
                        
                        (x, y) = _xy[str(i)]

                        try:
                            _url = self._image_helpers.get_presigned_url(img.src)
                            _r = requests.get(_url, stream=True)

                            if _r.status_code != 200:
                                print(f'presigned url: {_url}')
                                raise Exception('not 200 from aws - ' + str(_r.content))

                            _dest = 'tmp/' + img.src

                            with open(_dest, 'wb') as f:
                                shutil.copyfileobj(_r.raw, f)
                            self._pdf.image(_dest, x, y, 72, 90, type='png')
                        except:
                            traceback.print_exc()
                            self._pdf.set_xy(x - 5, y)
                            self._pdf.multi_cell(72, 10.0, _ascii_tree)
                        else:
                            os.remove(_dest)
                        finally:
                            self._pdf.set_font(self.__DEFAULT_FONT, 'B')
                            self._pdf.set_xy(x, y - self.__LINE_HEIGHT_PTS)
                            self._pdf.multi_cell(72, self.__LINE_HEIGHT_PTS, img.short)
                            self._pdf.set_xy(x, y + 90)
                            self._pdf.multi_cell(72, self.__LINE_HEIGHT_PTS, img.on[:10])
                            self._pdf.set_font('')
                            self._pdf.rect(x, y, 72, 90, 'D')

                    images = images[3:]
                    self._pdf.set_xy(_x, _y + 72 + (30 if images else 40))

            self.__this_page.append(_summary.split(',')[0])
            print(str(events) + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')

        self.__write_footer(self.__index_page, section='X', sub='A')
 
    def __write_appendix_b(self): # age at death

        self._pdf.add_page()
        self.__appendix_b_start = self._pdf.page_no()

        self._pdf.set_xy(72, 72)
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art('appendix b', font='ogre'))
        self._pdf.set_font('')

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, '\n[AGE AT DEATH]')
        self._pdf.set_font('')

        _column_number = 1
        _current_letter = ''

        def _first_page_of_appendix_b(self):
            return self._pdf.page_no() == self.__appendix_b_start

        for (_summary, _age) in self.__appendix_b:
            print(f'{_summary}')

            if not _age:
                print(f'  - not dead yet')
                continue

            if _summary[0].upper() != _current_letter:
                _current_letter = _summary[0].upper()

                # check if room for 1 + subheader + 1 + name
                if self._pdf.get_y() > ((72 * 10) - (10 * (1 + 1 + 1 + 1))):
                    print('new section overflows')
                
                    if _column_number == 1:
                        self.__write_gutter(8)
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72 + ((6 if _first_page_of_appendix_b(self) else 0) * 10))
                        _column_number = 2
                        print('***** SECOND COL *****')

                    elif _column_number == 2:
                        self.__write_footer(self.__index_page, section='X', sub='B')
                    
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

                _indexed_summary = _summary + ' ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (1 + 1 + len(_age) + len(_summary)))) + (' ' + _age)

                if len(_summary) > 27:
                    # if the summary line is wider than the column,
                    # then need to split the summary at the appropriate place
                    # and then put the dots and the page number on the next line
                    _split = _indexed_summary.find(' ', 30)

                    if _split == -1 and len(_summary) <= self.__COLUMN_WIDTH_CHARS:
                        _line_1 = _summary
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (1 + len(_age)))) + (' ' + _age)
                    elif _summary[_split:].strip() == '':
                        _line_1 = _summary[:_split]
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (1 + len(_age)))) + (' ' + _age)
                    else:
                        _line_1 = _summary[:_split]
                        _line_2 = _summary[_split:]
                        _line_2 = '   ' + _line_2 + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (3 + 2 + 2 + len(_line_2) + len(_age)))) + ('  ' + _age)

                    _indexed_summary = '\n'.join([_line_1, _line_2])

                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _indexed_summary)
                print(_summary + ' ' + _age + ' ' + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')


            elif _summary[0].upper() == _current_letter:
                # check if room for name
                if self._pdf.get_y() > ((72 * 10) - 10):
                    print('name overflows')
                
                    if _column_number == 1:
                        self.__write_gutter(8 if _first_page_of_appendix_b(self) else 1)
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72 + ((7 if _first_page_of_appendix_b(self) else 0) * 10))
                        _column_number = 2
                        print('***** SECOND COL *****')

                    elif _column_number == 2:
                        self.__write_footer(self.__index_page, section='X', sub='B')
                    
                        self._pdf.add_page()
                        self._pdf.set_xy(72, 72)
                        _column_number = 1
                        print('***** NEW   PAGE *****')
                        print('***** FIRST  COL *****')



                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
                
                _indexed_summary = _summary + ' ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (1 + 1 + len(_age) + len(_summary)))) + (' ' + _age)

                if len(_summary) > 27:
                    # if the summary line is wider than the column,
                    # then need to split the summary at the appropriate place
                    # and then put the dots and the page number on the next line
                    _split = _indexed_summary.find(' ', 30)

                    if _split == -1 and len(_summary) <= self.__COLUMN_WIDTH_CHARS:
                        _line_1 = _summary
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (1 + len(_age)))) + (' ' + _age)
                    elif _summary[_split:].strip() == '':
                        _line_1 = _summary[:_split]
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (1 + len(_age)))) + (' ' + _age)
                    else:
                        _line_1 = _summary[:_split]
                        _line_2 = _summary[_split:]
                        _line_2 = '   ' + _line_2 + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (3 + 2 + 2 + len(_line_2) + len(_age)))) + ('  ' + _age)

                    _indexed_summary = '\n'.join([_line_1, _line_2])

                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _indexed_summary)
                print(_summary + ' ' + _age + ' ' + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')

        self.__write_footer(self.__index_page, section='X', sub='B')
 
    def __write_appendix_c(self): # bloodlines

        self._pdf.add_page()
        self.__appendix_c_start = self._pdf.page_no()

        self._pdf.set_xy(72, 72)
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art('appendix c', font='ogre'))
        self._pdf.set_font('')

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, '\n[BLOODLINES]')
        self._pdf.set_font('')

        _column_number = 1
        _current_letter = ''

        def _first_page_of_appendix_c(self):
            return self._pdf.page_no() == self.__appendix_c_start

        def _generate_page_lookup(self):

            _lookup = { i:p for (s, p, i) in self.__index}
            return _lookup

        for (_summary, _page, _descendants) in self.__appendix_c:

            print(_summary)

            if not _descendants:
                print(f'  - middle of tree')
                continue 

            def _next_column(self):
                nonlocal _column_number
                if _column_number == 1:
                    self.__write_gutter(8 if _first_page_of_appendix_c(self) else 1)
                    self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72 + ((6 if _first_page_of_appendix_c(self) else 0) * 10))
                    _column_number = 2
                    print('***** SECOND COL *****')
                elif _column_number == 2:
                    self.__write_footer(self.__index_page, section='X', sub='C')
                    
                    self._pdf.add_page()
                    self._pdf.set_xy(72, 72)
                    _column_number = 1
                    print('***** NEW   PAGE *****')
                    print('***** FIRST  COL *****')

            def _apply_index(self, summary, page):

##
                _summary_with_index = summary + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + 2 + len(str(page)) + len(summary)))) + ('  ' + str(page))

                if len(summary) > 37:
                    # if the summary line is wider than the column, 
                    # then need to split the summary at the appropriate place 
                    # and then put the dots and page number on the next line
                    _split = _summary_with_index.find(' ', 30)
                    
                    if _split == -1 and len(summary) <= self.__COLUMN_WIDTH_CHARS:
                        _line_1 = summary
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + len(str(page))))) + ('  ' + str(page))
                    elif summary[_split:].strip() == '':
                        _line_1 = summary[:_split]
                        _line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + len(str(page))))) + ('  ' + str(page))
                    else:
                        _line_1 = summary[:_split]
                        _line_2 = summary[_split:]
                        _line_2 = '   ' + _line_2 + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (3 + 2 + 2 + len(_line_2) + len(str(page))))) + ('  ' + str(page))
                    _summary_with_index = '\n'.join([_line_1, _line_2])

                return _summary_with_index

##

            if _summary[0].upper() != _current_letter:
                _current_letter = _summary[0].upper()

                # check if room for 1 + subheader + 1 + 1 + 1 descendant
                if self._pdf.get_y() > ((72 * 10) - (10 * (1 + 1 + 1 + 1 + 1))):
                    print('new section overflows')
                    _next_column(self)

                # set header position
                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + (0 if self._pdf.get_y() == 72 else 10))
                # set header font + write header
                self._pdf.set_font(self.__DEFAULT_FONT, 'B')
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'[{_current_letter.upper()}]')
                self._pdf.set_font('')

                print(_current_letter + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
                
                # add spacing before rows
                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)
                # ancestor listed in bold
                self._pdf.set_font(self.__DEFAULT_FONT, 'B')
 
                # self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _summary)
                # self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
                # self._pdf.set_font('')

                _summary_with_index = _apply_index(self, _summary, _page)

                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _summary_with_index)
                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
                self._pdf.set_font('')



                for (ix, kin, _id) in _descendants:

                    if self._pdf.get_y() > ((72 * 10) - (10 * (1 + 1))):
                        print('new section overflows')
                        _next_column(self)

                    _lookup = _generate_page_lookup(self)
                    _with_index = _apply_index(self, f'{"."*ix}{kin}', _lookup.get(_id))
                    self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _with_index)
                    self._pdf.set_font('')
                    print(f'{"."*ix}{kin}')
                    self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
               

            elif _summary[0].upper() == _current_letter:
                # check if room for name + 1 descendant

                if self._pdf.get_y() > ((72 * 10) - (10 * (1 + 1 + 1))):
                    print('name overflows')
                    _next_column(self)

                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)
 

                # ancestor listed in bold
                self._pdf.set_font(self.__DEFAULT_FONT, 'B')

                _summary_with_index = _apply_index(self, _summary, _page)

                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _summary_with_index)
                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
                self._pdf.set_font('')

                for (ix, kin, _id) in _descendants:
                    if self._pdf.get_y() > ((72 * 10) - (10)):
                        print('new section overflows')
                        _next_column(self)

                    _lookup = _generate_page_lookup(self)
                    _with_index = _apply_index(self, f'{"."*ix}{kin}', _lookup.get(_id))
                    self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _with_index)
                    self._pdf.set_font('')
                    print(f'{"."*ix}{kin}')
                    self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
                
                
        # write page number at bottom of page
        self.__write_footer(self.__index_page, section='X', sub='C')

    def __write_appendix_d(self):

        self._pdf.add_page()
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')

        self._pdf.set_xy(72, 72)
 
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art('appendix d', font='ogre'))
        self._pdf.set_font('')

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, '\n[GRAVESTONE ARCHIIVE]')
        self._pdf.set_font('')

        _x = 72
        _y = self._pdf.get_y() + 20

        images = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]

        while images:

            if _y + 10 + 90 + 20 > (72 * 10):
                # next page
                self.__write_footer(self.__index_page, section='X', sub='D')
                    
                self._pdf.add_page()
                _x = 72
                _y = 72
                print('***** NEW   PAGE *****')

            _xy = {}
            _xy['0'] = (_x, _y + 10)
            _xy['1'] = (_x + 144 + 18, _y + 10)
            _xy['2'] = (_x + 144 + 18 + 144 + 18, _y + 10)

            #  | --- 144 --- | 18 |--- 144 --- | 18 | --- 144 --- |

            #     /\      
            #    /\*\     
            #   /\O\*\    
            #  /*/\/\/\   
            # /\O\/\*\/\  
            #     ||      
            #     ||      
            #     ||      
                    
            _ascii_tree = '' + '\n'
            _ascii_tree += '      /\\      '*2 + '\n'      
            _ascii_tree += '     /\\*\\     '*2 + '\n'     
            _ascii_tree += '    /\\O\\*\\    '*2 + '\n'    
            _ascii_tree += '   /*/\\/\\/\\   '*2 + '\n'   
            _ascii_tree += '  /\\O\\/\\*\\/\\  '*2 + '\n'
            _ascii_tree += '      ||      '*2 + '\n'
            _ascii_tree += '      ||      '*2

            for i, img in enumerate(images[:3]):
                        
                (x, y) = _xy[str(i)]

                if y + 10 + 90 + 20 > (72 * 10):
                    # next page
                    self.__write_footer(self.__index_page, section='X', sub='D')
                    
                    self._pdf.add_page()
                    self._pdf.set_xy(72, 72)
                    print('***** NEW   PAGE *****')

                try:
                    _url = self._image_helpers.get_presigned_url(img.src)
                    _r = requests.get(_url, stream=True)

                    if _r.status_code != 200:
                        print(f'presigned url: {_url}')
                        raise Exception('not 200 from aws - ' + str(_r.content))

                    _dest = 'tmp/' + img.src

                    with open(_dest, 'wb') as f:
                        shutil.copyfileobj(_r.raw, f)
                    self._pdf.image(_dest, x, y, 144, 90, type='png')
                except:
                    traceback.print_exc()
                    self._pdf.set_xy(x, y)
                    self._pdf.multi_cell(144, 10.0, _ascii_tree)
                else:
                    os.remove(_dest)
                finally:
                    self._pdf.set_font(self.__DEFAULT_FONT, 'B')
                    self._pdf.set_xy(x, y - self.__LINE_HEIGHT_PTS)
                    self._pdf.multi_cell(144, self.__LINE_HEIGHT_PTS, 'short') #img.short)
                self._pdf.set_xy(x, y + 90)
                self._pdf.multi_cell(90, self.__LINE_HEIGHT_PTS, f'on {img}') #img.on[:10])
                self._pdf.set_font('')
                self._pdf.rect(x, y, 144, 90, 'D')
                print(f'printed img {img}')

            images = images[3:]
            _x = 72 
            _y = _y + 90 + (30 if images else 40)

        self.__write_footer(self.__index_page, section='X', sub='D')
 
    def __write_appendix_e(self): # etymology/origins of names

        self._pdf.add_page()
        self.__appendix_e_start = self._pdf.page_no()

        self._pdf.set_xy(72, 72)
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art('appendix e', font='ogre'))
        self._pdf.set_font('')

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.set_font(self.__DEFAULT_FONT, 'B')
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, '\n[ETYMOLOGIES/ORIGINS OF NAMES]')
        self._pdf.set_font('')

        _column_number = 1
        _current_letter = ''

        def _first_page_of_appendix_e(self):
            return self._pdf.page_no() == self.__appendix_e_start

        for (_summary, _names) in self.__appendix_e:
            print(f'{_summary}')
            print('.')

            __names = _names.as_list
            print('__names')
            print(__names)


            def create_aligned_text(rows):
                _aligned = []
                while rows:
                    r = rows.pop(0)

                    leading = len(r) - len(r.lstrip())
                    r = r.strip()
                    if (len(r) + leading) <= 43:
                        _aligned.append((' ' * leading) + r)
                        continue

                    r = r.split(' ')
                    _words = ' ' * leading
                    while r:
                        _words += ' ' if len(_words) > leading else ''
                        _w = r.pop(0)
                        print(_w)
                        _words += _w if len(_words) + len(_w) <= 43 else ''

                        if not _words.endswith(_w):
                            r.insert(0, _w)
                            _aligned.append(_words)
                            _words = ' ' * (leading + 2)
                            continue

                    _aligned.append(_words)
                        
                return _aligned

            __names = [create_aligned_text(e) for e in _names.as_list]

            print('.')
            for e in __names:
                print(e)

            ############################################
            #
            # MUSKIVITCH, JENNA K (f) (yyyy-?)         *
            #
            #   "Jenna": 4# 1 + (1+1) + 1 + (2+3+1) + 1 + (1+2) + 1 + (1+1)
            #       english for "Jenny", "Jennifer"
            #       means "fair, magical being"
            #   
            #       welsh for "Guinevere", 
            #           "Gweenhwyfar"
            #       translations: 
            #           'Gwen' (white, fair)
            #           'hwyfar' (smooth, soft)
            #       means "fair one", "white shadow"
            #
            #       greek for "Jane", "Janet"
            #       means "paradise", "little bird", 
            #           "heaven"
            #
            #       arabic/hebrew translations:
            #           "little bird"
            #
            # MUSKIVITCH, JENNA K (f) (yyyy-?)
            # Continued...
            #
            #   "Karen": 1# 1 + (3)
            #       named after late maternal 
            #       grandmother, WOLBERS, KAREN LEE 
            #       (1957-2004)
            #
            ###########################################

            def _next_column(self):
                nonlocal _column_number
                if _column_number == 1:
                    self.__write_gutter(8 if _first_page_of_appendix_e(self) else 1)
                    self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72 + ((6 if _first_page_of_appendix_e(self) else 0) * 10))
                    _column_number = 2
                    print('***** SECOND COL *****')
                elif _column_number == 2:
                    self.__write_footer(self.__index_page, section='X', sub='E')
                    
                    self._pdf.add_page()
                    self._pdf.set_xy(72, 72)
                    _column_number = 1
                    print('***** NEW   PAGE *****')
                    print('***** FIRST  COL *****')

            if _summary[0].upper() != _current_letter:
                _current_letter = _summary[0].upper()

                # check if room for 1 + subheader + 1 + name + group1
                if self._pdf.get_y() > ((72 * 10) - (10 * (1 + 1 + 1 + 1 + len(__names[0])))):
                    print('new section overflows')
                    _next_column()

                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + (0 if self._pdf.get_y() == 72 else 10))
                
                self._pdf.set_font(self.__DEFAULT_FONT, 'B')
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'[{_current_letter.upper()}]')
                self._pdf.set_font('')

                print(_current_letter + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)
            
                
                _indexed_summary = _summary

                self._pdf.set_font(self.__DEFAULT_FONT, 'B') 
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _indexed_summary)
                self._pdf.set_font('')
           
                print('1278')
                print(_column_number)

                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
 
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, '\n'.join(__names.pop(0)))

                print('__names is')
                print(__names)

                while __names:
                
                    if self._pdf.get_y() > ((72 * 10) - (10 * (1 + len(__names[0])))):
                        print('overflows...')
                        _next_column()
                
                    self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
 
                    self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, '\n'.join(__names.pop(0)))

                  


                #print(_summary + ' ' + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')


            elif _summary[0].upper() == _current_letter:
                # check if room for name

                if self._pdf.get_y() > ((72 * 10) - (10 * (1 + 1 + len(__names[0])))):
                    print('new section overflows')
                    _next_column()


                '''
                if self._pdf.get_y() > ((72 * 10) - 10):
                    print('name overflows')
                
                    if _column_number == 1:
                        self.__write_gutter(8 if _first_page_of_appendix_e(self) else 1)
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72 + ((7 if _first_page_of_appendix_e(self) else 0) * 10))
                        _column_number = 2
                        print('***** SECOND COL *****')

                    elif _column_number == 2:
                        self.__write_footer(self.__index_page, section='X', sub='E')
                    
                        self._pdf.add_page()
                        self._pdf.set_xy(72, 72)
                        _column_number = 1
                        print('***** NEW   PAGE *****')
                        print('***** FIRST  COL *****')
                '''


                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)
                
                _indexed_summary = _summary
                #_indexed_summary = _summary + ' ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (1 + 1 + len(_age) + len(_summary)))) + (' ' + _age)

                if len(_summary) > 27:
                    # if the summary line is wider than the column,
                    # then need to split the summary at the appropriate place
                    # and then put the dots and the page number on the next line
                    _split = _indexed_summary.find(' ', 30)

                    if _split == -1 and len(_summary) <= self.__COLUMN_WIDTH_CHARS:
                        _line_1 = _summary
                        #_line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (1 + len(_age)))) + (' ' + _age)
                    elif _summary[_split:].strip() == '':
                        _line_1 = _summary[:_split]
                        #_line_2 = ('.'*(self.__COLUMN_WIDTH_CHARS - (1 + len(_age)))) + (' ' + _age)
                    else:
                        _line_1 = _summary[:_split]
                        #_line_2 = _summary[_split:]
                        #_line_2 = '   ' + _line_2 + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (3 + 2 + 2 + len(_line_2) + len(_age)))) + ('  ' + _age)

                    _line_2 = ''
                    _indexed_summary = '\n'.join([_line_1, _line_2])


                self._pdf.set_font(self.__DEFAULT_FONT, 'B') 
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _indexed_summary)
                self._pdf.set_font('')
           
                print(_column_number)

                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
 
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, '\n'.join(__names.pop(0)))

                print('__names is')
                print(__names)

                while __names:
                
                    if self._pdf.get_y() > ((72 * 10) - (10 * (1 + len(__names[0])))):
                        print('overflows...')
                        _next_column()
                
                    self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y())
 
                    self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, '\n'.join(__names.pop(0)))


                print(_summary + ' ' + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')

        self.__write_footer(self.__index_page, section='X', sub='E')
 

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


