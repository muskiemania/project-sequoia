import datetime
import string
import random

import art
import fpdf
import requests
import textwrap
import roman

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
        self.__LINE_HEIGHT_PTS = 10.0
        self.__SINGLE_COLUMN_WIDTH_IN = 6.5
        self.__DUAL_COLUMN_WIDTH_IN = 3.0
        self.__GUTTER_X_IN = 4.0
        self.__GUTTER_WIDTH_IN = 0.5
        self.__FIRST_COLUMN_X_IN = 1.0
        self.__SECOND_COLUMN_X_IN = 4.5
        self.__TOP_PTS = 72

    def init(self):
        self._pdf.set_auto_page_break(False)
        self._pdf.set_font('Courier', '', 8.0)
        self.__wrapper = textwrap.TextWrapper()
        self.__wrapper.width = self.__COLUMN_WIDTH_CHARS
        
        self.__write_title_page()

        self.__first_chapter = True

        return self

    def __page_number(self):
        return self._pdf.page_no() - 1

    def __index_page(self):
        return roman.toRoman(self._pdf.page_no() - self.__index_start).lower()

    def write_chapter(self, chapter, people, _begin_chapter=True):

        if self.__first_chapter:
            self._pdf.add_page()
            self._pdf.set_xy(self.__TOP_PTS, self.__TOP_PTS)
            self.__column_number = 1
            self.__first_chapter = False

        for person in people:
            _synopsis = str(person)
        
            if _begin_chapter:
                _chapter_title = art.text2art(chapter, 'ogre')
                _wrapped_sentence = self.__wrapper.fill(_synopsis)

                _lines_chapter_title = len(_chapter_title.split('\r\n'))
                _lines_wrapped_sentence = 1 + len(_wrapped_sentence.split('\n'))
            
                if self._pdf.get_y() > ((72 * self.__LINE_HEIGHT_PTS) - (self.__LINE_HEIGHT_PTS * (1 + _lines_chapter_title + 1 + 1 + _lines_wrapped_sentence))):
                    if self.__column_number == 1:
                        self._pdf.set_xy(72 * self.__GUTTER_X_IN, 72)
                        self._pdf.multi_cell(72 * self.__GUTTER_WIDTH_IN, self.__LINE_HEIGHT_PTS, '\n'.join(['|' for _ in range(64)]), 0, 'C')
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72)
                        self.__column_number = 2
                        print('***** SECOND COL *****')

                    elif self.__column_number == 2:
                        self._pdf.set_xy(72, 52)
                        self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, f'{self.__this_page[0]}...')
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 52)
                        self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, f'...{self.__this_page[-1]}', 0, 'R')
                        self._pdf.set_xy(72, (10 * 72) + 20)
                        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, f'-- Page {self.__page_number()} --', 0, 'C')
                    
                        self._pdf.add_page()
                        self.__this_page = []
                        self._pdf.set_xy(72, 72)
                        self.__column_number = 1
                        print('***** NEW   PAGE *****')
                        print('***** FIRST  COL *****')

                self._pdf.set_xy(72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + (0 if self._pdf.get_y() == 72 else 10))
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, _chapter_title)
                print(_chapter_title + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
                self._pdf.set_xy(72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, self.__LINE_HEIGHT_PTS, '\n'.join([person.extended, _wrapped_sentence]))
                self.__this_page.append(person.summary.split(',')[0])
                print(_wrapped_sentence + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
                self.__index.append((person.summary, self.__page_number()))
                _begin_chapter = False

            else:
                _wrapped_sentence = self.__wrapper.fill(_synopsis)

                _lines_wrapped_sentence = len(_wrapped_sentence.split('\n'))
                if self._pdf.get_y() > ((72 * 10) - (10 * (1 + _lines_wrapped_sentence))):

                    if self.__column_number == 1:
                        self._pdf.set_xy(72 * self.__GUTTER_X_IN, 72)
                        self._pdf.multi_cell(72 * self.__GUTTER_WIDTH_IN, 10.0, '\n'.join(['|' for _ in range(64)]), 0, 'C')
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 72)
                        self.__column_number = 2
                        print('***** SECOND COL *****')

                    elif self.__column_number == 2:
                        self._pdf.set_xy(72, 52)
                        self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'{self.__this_page[0]}...')
                        self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 52)
                        self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'...{self.__this_page[-1]}', 0, 'R')
                        self._pdf.set_xy(72, (10 * 72) + 20)
                        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, f'-- Page {self.__page_number()} --', 0, 'C')
 
                        self._pdf.add_page()
                        self.__this_page = []
                        self._pdf.set_xy(72, 72)
                        self.__column_number = 1
                        print('***** NEW   PAGE *****')
                        print('***** FIRST  COL *****')


                self._pdf.set_xy(72 if self.__column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + (0 if self._pdf.get_y() == 72 else 10))
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, '\n'.join([person.extended, _wrapped_sentence]))
                self.__this_page.append(person.summary.split(',')[0])
                self.__index.append((person.summary, self.__page_number()))
                print(_wrapped_sentence + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
 
    def complete(self):
        if self.__this_page:
            self._pdf.set_xy(72, 52)
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'{self.__this_page[0]}...')
            self._pdf.set_xy(72 * self.__SECOND_COLUMN_X_IN, 52)
            self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'...{self.__this_page[-1]}', 0, 'R')
            self._pdf.set_xy(72, (10 * 72) + 20)
            self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, f'-- Page {self.__page_number()} --', 0, 'C')
 
        self.__write_index()

        self._pdf.output('sample_fpdf.pdf', 'F')

    def __write_index(self):

        self.__index_start = self._pdf.page_no()
        self._pdf.add_page()

        self._pdf.set_xy(72, 72)
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, art.text2art('index', font='ogre'))
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
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, f'[{_current_letter.upper()}]')
                print(_current_letter + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
                self._pdf.set_xy(72 if _column_number == 1 else 72 * self.__SECOND_COLUMN_X_IN, self._pdf.get_y() + 10)
                
                _indexed_summary = summary + '  ' + ('.'*(self.__COLUMN_WIDTH_CHARS - (2 + 2 + len(str(page_num)) + len(summary)))) + ('  ' + str(page_num))
        
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
                
                self._pdf.multi_cell(72 * self.__DUAL_COLUMN_WIDTH_IN, 10.0, _indexed_summary)
                print(summary + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')

        self._pdf.set_xy(72, (10 * 72) + 20)
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, f'-- {self.__index_page()} --', 0, 'C')
 
        while self._pdf.page_no() % 4 > 0:
            self._pdf.add_page()

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
        MMMMMMMMMMMMMNOdxk0WMMMMMMMMMMMMMM
        MMMMMMMMMMMWKdlllloxKWMMMMMMMMMMMM
        MMMMMMMMMMNkollllllloONMMMMMMMMMMM
        MMMMMMMMWKxolllllllllld0WMMMMMMMMM
        MMMMMMMW0dooooolooooooookXMMMMMMMM
        MMMMMMNOoooooooooooooooooxXMMMMMMM
        MMMMMMWKOOxolooooooooodO0XWMMMMMMM
        MMMMMMMMWKdlllllllooood0WMMMMMMMMM
        MMMMMMMNOololllllllllllokXMMMMMMMM
        MMMMMMXxolllollllllllloood0NMMMMMM
        MMMMMKdllllllllllllllloolloONMMMMM
        MMMMMX0Okolllllllllllllld0XNWMMMMM
        MMMMMMMNkollllllllllllllokXMMMMMMM
        MMMMMWKxooooooooooooooooold0NMMMMM
        MMMMNOdoooooooooooooooooooooxKWMMM
        MMMNkdoooooooooooooooooooooooxXMMM
        MMMNOkkxxxxxddddooddxxkkkOO00XWMMM
        MMMMMWWWWNNNNNKxooxKNWWWMMMMMMMMMM
        MMMMMMMMMMMMMMKdoodKMMMMMMMMMMMMMM
        MMMMMMMMMMMMMMXkxxkKMMMMMMMMMMMMMM
        """
        _two_trees = _tree.split('\n')
        _two_trees = [t.strip().replace('M', ' ') for t in _two_trees]
        _two_trees = '\n'.join([t + '     ' + t for t in _two_trees])
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * self.__SINGLE_COLUMN_WIDTH_IN, 10.0, _two_trees, 0,'C')


