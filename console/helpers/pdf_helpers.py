import datetime
import string
import random

import art
import fpdf
import requests
import textwrap

class PDFHelpers:

    def __init__(self):
        self._pdf = fpdf.FPDF(format='Letter', unit='pt')
        self.__this_page = []
        self.__index = []
        self.__column_number = None
        self.__wrapper = None
        self.__first_chapter = False

    def init(self):
        self._pdf.set_auto_page_break(False)
        self._pdf.set_font('Courier', '', 8.0)
        self.__wrapper = textwrap.TextWrapper()
        self.__wrapper.width = 40
        
        self.__write_title_page()

        self.__first_chapter = True

        return self

    def write_chapter(self, chapter, people, _begin_chapter=True):

        if self.__first_chapter:
            self._pdf.add_page()
            self._pdf.set_xy(72, 72)
            self.__column_number = 1
            self.__first_chapter = False

        for person in people:
            _synopsis = str(person)
        
            if _begin_chapter:
                _chapter_title = art.text2art(chapter, 'ogre')
                _wrapped_sentence = self.__wrapper.fill(_synopsis)

                _lines_chapter_title = len(_chapter_title.split('\r\n'))
                _lines_wrapped_sentence = len(_wrapped_sentence.split('\n'))
                print(f'new chapter: y is {self._pdf.get_y()}, title is {_lines_chapter_title} sentence is {_lines_wrapped_sentence}')
                print((72 * 10) - (10 * (_lines_chapter_title + 1 + _lines_wrapped_sentence)))
            
                if self._pdf.get_y() > ((72 * 10) - (10 * (1 + _lines_chapter_title + 1 + _lines_wrapped_sentence))):
                
                    print('new chapter overflows')
                
                    if self.__column_number == 1:
                        self._pdf.set_xy(4.75 * 72, 72)
                        self.__column_number = 2
                        print('***** SECOND COL *****')

                    elif self.__column_number == 2:
                        self._pdf.set_xy(72, 52)
                        self._pdf.multi_cell(72 * 2.75, 10.0, f'{_this_page[0]}...')
                        self._pdf.set_xy(72 * 4.75, 52)
                        self._pdf.multi_cell(72 * 2.75, 10.0, f'...{_this_page[-1]}', 0, 'R')
                        self._pdf.set_xy(72, (10 * 72) + 20)
                        self._pdf.multi_cell(72 * 6.5, 10.0, f'-- Page {_pdf.page_no()} --', 0, 'C')
                    
                        self._pdf.add_page()
                        self.__this_page = []
                        self._pdf.set_xy(72, 72)
                        self._column_number = 1
                        print('***** NEW   PAGE *****')
                        print('***** FIRST  COL *****')

                self._pdf.set_xy(72 if self.__column_number == 1 else 72 * 4.75, self._pdf.get_y() + (0 if self._pdf.get_y() == 72 else 10))
                self._pdf.multi_cell(72 * 2.75, 10.0, _chapter_title)
                print(_chapter_title + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
                self._pdf.set_xy(72 if self.__column_number == 1 else 72 * 4.75, self._pdf.get_y() + 10)
                self._pdf.multi_cell(72 * 2.75, 10.0, _wrapped_sentence)
                self.__this_page.append(_wrapped_sentence.split(' ')[0])
                print(_wrapped_sentence + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
                _begin_chapter = False

            else:
                _wrapped_sentence = self.__wrapper.fill(_synopsis)

                _lines_wrapped_sentence = len(_wrapped_sentence.split('\n'))
                print(f'not new chapter: y is {self._pdf.get_y()}, sentence is {_lines_wrapped_sentence}')
                print((72 * 10) - (10 * _lines_wrapped_sentence))
                if self._pdf.get_y() > ((72 * 10) - (10 * _lines_wrapped_sentence)):

                    print('next sentence overflows')

                    if self.__column_number == 1:
                        self._pdf.set_xy(4.75 * 72, 72)
                        self.__column_number = 2
                        print('***** SECOND COL *****')

                    elif self.__column_number == 2:
                        self._pdf.set_xy(72, 52)
                        self._pdf.multi_cell(72 * 2.75, 10.0, f'{_this_page[0]}...')
                        self._pdf.set_xy(72 * 4.75, 52)
                        self._pdf.multi_cell(72 * 2.75, 10.0, f'...{_this_page[-1]}', 0, 'R')
                        self._pdf.set_xy(72, (10 * 72) + 20)
                        self._pdf.multi_cell(72 * 6.5, 10.0, f'-- Page {_pdf.page_no()} --', 0, 'C')
 
                        self._pdf.add_page()
                        self.__this_page = []
                        self._pdf.set_xy(72, 72)
                        self.__column_number = 1
                        print('***** NEW   PAGE *****')
                        print('***** FIRST  COL *****')


                self._pdf.set_xy(72 if self.__column_number == 1 else 72 * 4.75, self._pdf.get_y() + (0 if self._pdf.get_y() == 72 else 10))
                self._pdf.multi_cell(72 * 2.75, 10.0, _wrapped_sentence)
                self.__this_page.append(_wrapped_sentence.split(' ')[0])
                print(_wrapped_sentence + f' x: {self._pdf.get_x()}, y: {self._pdf.get_y()}')
 

    def complete(self):
        if self.__this_page:
            self._pdf.set_xy(72, 52)
            self._pdf.multi_cell(72 * 2.75, 10.0, f'{self.__this_page[0]}...')
            self._pdf.set_xy(72 * 4.75, 52)
            self._pdf.multi_cell(72 * 2.75, 10.0, f'...{self.__this_page[-1]}', 0, 'R')
            self._pdf.set_xy(72, (10 * 72) + 20)
            self._pdf.multi_cell(72 * 6.5, 10.0, f'-- Page {self._pdf.page_no()} --', 0, 'C')
 
        self._pdf.output('sample_fpdf.pdf', 'F')

    def __write_title_page(self, prepared_for='muskiemania'):
        self._pdf.add_page()

        self._pdf.set_xy(72, 72)
        self._pdf.multi_cell(72 * 6.5, 10.0, art.text2art('project', font='georgia11'))

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * 6.5, 30.0, art.text2art(' ', font='sequoia'), 0, 'C')

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * 6.5, 10.0, art.text2art('   sequoia', font='georgia11'), 0, 'R')

        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * 6.5, 10.0, art.text2art(f' ', font='mini'), 0, 'C')
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * 6.5, 10.0, art.text2art(f'prepared for:', font='mini'), 0, 'C')
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * 6.5, 10.0, art.text2art(f'{prepared_for}', font='mini'), 0, 'C')
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * 6.5, 10.0, art.text2art(f'on {datetime.datetime.now().strftime("%B %d, %Y")}', font='mini'), 0, 'C')
        self._pdf.set_xy(72, self._pdf.get_y())
        self._pdf.multi_cell(72 * 6.5, 10.0, art.text2art(f' ', font='mini'), 0, 'C')
 
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
        self._pdf.multi_cell(72 * 6.5, 10.0, _two_trees, 0,'C')


