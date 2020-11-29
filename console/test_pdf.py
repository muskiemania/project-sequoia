import art
import fpdf

import string
import requests
import random
import textwrap

_pdf = fpdf.FPDF(format='Letter', unit='pt')
_pdf.set_auto_page_break(False)
_pdf.add_page()
_pdf.set_font('Courier', '', 8.0)

_pdf.set_xy(72, 72)
_pdf.multi_cell(72 * 6.5, 10.0, art.text2art('project', font='georgia11'))

_pdf.set_xy(72, _pdf.get_y())
_pdf.multi_cell(72 * 6.5, 30.0, art.text2art(' ', font='sequoia'), 0, 'C')

_pdf.set_xy(72, _pdf.get_y())
_pdf.multi_cell(72 * 6.5, 10.0, art.text2art('   sequoia', font='georgia11'), 0, 'R')

_pdf.set_xy(72, _pdf.get_y())
_pdf.multi_cell(72 * 6.5, 10.0, art.text2art(''' 
    prepared for:
    muskiemania
    on November 28, 2020
     ''', font='mini'), 0, 'C')

_tree = """
MMMMMMMMMMMMMMMMNOdxk0WMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMWKdlllloxKWMMMMMMMMMMMMMMM
MMMMMMMMMMMMMNkollllllloONMMMMMMMMMMMMMM
MMMMMMMMMMMWKxolllllllllld0WMMMMMMMMMMMM
MMMMMMMMMMW0dooooolooooooookXMMMMMMMMMMM
MMMMMMMMMNOoooooooooooooooooxXMMMMMMMMMM
MMMMMMMMMWKOOxolooooooooodO0XWMMMMMMMMMM
MMMMMMMMMMMWKdlllllllooood0WMMMMMMMMMMMM
MMMMMMMMMMNOololllllllllllokXMMMMMMMMMMM
MMMMMMMMMXxolllollllllllloood0NMMMMMMMMM
MMMMMMMMKdllllllllllllllloolloONMMMMMMMM
MMMMMMMMX0Okolllllllllllllld0XNWMMMMMMMM
MMMMMMMMMMNkollllllllllllllokXMMMMMMMMMM
MMMMMMMMWKxooooooooooooooooold0NMMMMMMMM
MMMMMMMNOdoooooooooooooooooooooxKWMMMMMM
MMMMMMNkdoooooooooooooooooooooooxXMMMMMM
MMMMMMNOkkxxxxxddddooddxxkkkOO00XWMMMMMM
MMMMMMMMWWWWNNNNNKxooxKNWWWMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMKdoodKMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMXkxxkKMMMMMMMMMMMMMMMMM
"""
_tree = _tree.replace('M', ' ')
_two_trees = _tree.split('\n')
_two_trees = '\n'.join([t+t for t in _two_trees])
_pdf.set_xy(72, _pdf.get_y())
_pdf.multi_cell(72 * 6.5, 10.0, _two_trees, 0,'C')

###

chapters = sorted(random.sample(string.ascii_lowercase, random.randint(5, 9)), reverse=True)
WORDS = requests.get('https://www.mit.edu/~ecprice/wordlist.10000').content.splitlines()
WORDS = [w.decode('utf-8') for w in WORDS]

_next_chapter = True
_column_number = 1

print(chapters)

_pdf.add_page()
_pdf.set_xy(72, 72)
print('***** NEW   PAGE *****')
print('***** FIRST  COL *****')

wrapper = textwrap.TextWrapper()
wrapper.width=40

_this_page = []

while chapters:
    _chapter = chapters.pop()
    _items = ['x' for i in range(5, 9)]

    while _items:
        _items.pop()
        _sentence = ' '.join(random.choices(WORDS, k=random.randint(50, 90)))

        # if _next_chapter, must check to see if chapter title + _sentence will exceed remaining height...
        # if not, then write title, then write _sentence
        # if so, must either move to next column, OR move to next page

        if _next_chapter:
            _chapter_title = art.text2art(_chapter, 'ogre')
            _wrapped_sentence = wrapper.fill(_sentence)

            _lines_chapter_title = len(_chapter_title.split('\r\n'))
            _lines_wrapped_sentence = len(_wrapped_sentence.split('\n'))
            print(f'new chapter: y is {_pdf.get_y()}, title is {_lines_chapter_title} sentence is {_lines_wrapped_sentence}')
            print((72 * 10) - (10 * (_lines_chapter_title + 1 + _lines_wrapped_sentence)))
            if _pdf.get_y() > ((72 * 10) - (10 * (1 + _lines_chapter_title + 1 + _lines_wrapped_sentence))):
                
                print('new chapter overflows')
                
                if _column_number == 1:
                    _pdf.set_xy(4.75 * 72, 72)
                    _column_number = 2
                    print('***** SECOND COL *****')

                elif _column_number == 2:
                    _pdf.set_xy(72, 52)
                    _pdf.multi_cell(72 * 2.75, 10.0, f'{_this_page[0]}...')
                    _pdf.set_xy(72 * 4.75, 52)
                    _pdf.multi_cell(72 * 2.75, 10.0, f'...{_this_page[-1]}', 0, 'R')
                    _pdf.set_xy(72, (10 * 72) + 20)
                    _pdf.multi_cell(72 * 6.5, 10.0, f'-- Page {_pdf.page_no()} --', 0, 'C')
                    
                    _pdf.add_page()
                    _this_page = []
                    _pdf.set_xy(72, 72)
                    _column_number = 1
                    print('***** NEW   PAGE *****')
                    print('***** FIRST  COL *****')

            _pdf.set_xy(72 if _column_number == 1 else 72 * 4.75, _pdf.get_y() + (0 if _pdf.get_y() == 72 else 10))
            _pdf.multi_cell(72 * 2.75, 10.0, _chapter_title)
            print(_chapter_title + f' x: {_pdf.get_x()}, y: {_pdf.get_y()}')
            _pdf.set_xy(72 if _column_number == 1 else 72 * 4.75, _pdf.get_y() + 10)
            _pdf.multi_cell(72 * 2.75, 10.0, _wrapped_sentence)
            _this_page.append(_wrapped_sentence.split(' ')[0])
            print(_wrapped_sentence + f' x: {_pdf.get_x()}, y: {_pdf.get_y()}')
            _next_chapter = False

        else:
            _wrapped_sentence = wrapper.fill(_sentence)

            _lines_wrapped_sentence = len(_wrapped_sentence.split('\n'))
            print(f'not new chapter: y is {_pdf.get_y()}, sentence is {_lines_wrapped_sentence}')
            print((72 * 10) - (10 * _lines_wrapped_sentence))
            if _pdf.get_y() > ((72 * 10) - (10 * _lines_wrapped_sentence)):

                print('next sentence overflows')

                if _column_number == 1:
                    _pdf.set_xy(4.75 * 72, 72)
                    _column_number = 2
                    print('***** SECOND COL *****')

                elif _column_number == 2:
                    _pdf.set_xy(72, 52)
                    _pdf.multi_cell(72 * 2.75, 10.0, f'{_this_page[0]}...')
                    _pdf.set_xy(72 * 4.75, 52)
                    _pdf.multi_cell(72 * 2.75, 10.0, f'...{_this_page[-1]}', 0, 'R')
                    _pdf.set_xy(72, (10 * 72) + 20)
                    _pdf.multi_cell(72 * 6.5, 10.0, f'-- Page {_pdf.page_no()} --', 0, 'C')
 
                    _pdf.add_page()
                    _this_page = []
                    _pdf.set_xy(72, 72)
                    _column_number = 1
                    print('***** NEW   PAGE *****')
                    print('***** FIRST  COL *****')


            _pdf.set_xy(72 if _column_number == 1 else 72 * 4.75, _pdf.get_y() + (0 if _pdf.get_y() == 72 else 10))
            _pdf.multi_cell(72 * 2.75, 10.0, _wrapped_sentence)
            _this_page.append(_wrapped_sentence.split(' ')[0])
            print(_wrapped_sentence + f' x: {_pdf.get_x()}, y: {_pdf.get_y()}')
 
    _next_chapter = True    

if _this_page:
    _pdf.set_xy(72, 52)
    _pdf.multi_cell(72 * 2.75, 10.0, f'{_this_page[0]}...')
    _pdf.set_xy(72 * 4.75, 52)
    _pdf.multi_cell(72 * 2.75, 10.0, f'...{_this_page[-1]}', 0, 'R')
    _pdf.set_xy(72, (10 * 72) + 20)
    _pdf.multi_cell(72 * 6.5, 10.0, f'-- Page {_pdf.page_no()} --', 0, 'C')
 
_pdf.output('sample_fpdf.pdf', 'F')

