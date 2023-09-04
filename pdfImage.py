import fitz
from PIL import Image
from utils import *
from whoosh.analysis import Tokenizer, Token
import jieba
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
import os
import shutil
import tempfile

LOGO_WIDTH = 398
LOGO_HEIGHT = 137


class ChineseTokenizer(Tokenizer):
    def __call__(self, value, positions=False, chars=False,
                 keeporiginal=False, removestops=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        t = Token(positions, chars, removestops=removestops, mode=mode,
                  **kwargs)
        seglist = jieba.cut(value, cut_all=True)
        for w in seglist:
            t.original = t.text = w
            t.boost = 1.0
            if positions:
                t.pos = start_pos + value.find(w)
            if chars:
                t.startchar = start_char + value.find(w)
            if chars and positions:
                t.endchar = start_char + value.find(w) + len(w)
            yield t


def ChineseAnalyzer():
    return ChineseTokenizer()


def load_pdf(file, dpi=300, skip_page_front=0, skip_page_back=1, skip_block=5, lang='CN'):
    """
    Load pdf file, covert to image, description and index it
    :param lang:
    :param skip_block:
    :param skip_page_back:
    :param skip_page_front:
    :param dpi:
    :param file:
    :return:
    """

    doc = fitz.open(file)

    # load pages
    pages = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        pages.append(page)

    # increase dpi to 300
    dpi = int(dpi)
    scale = dpi / 72  # default dpi of pdf is 72
    matrix = fitz.Matrix(scale, scale)
    skip_block = int(skip_block)

    # base_name = os.path.basename(file).split('.')[0]
    # path_name = f'images{base_name}'
    # if os.path.exists(path_name):
    #     shutil.rmtree(path_name)
    # os.mkdir(path_name)
    temp_image_dir = tempfile.mkdtemp(prefix='images_')

    for page in pages[int(skip_page_front):-int(skip_page_back)]:  # skip final page

        p1dict = page.get_text('dict')
        blocks = p1dict['blocks']
        page_pix = page.get_pixmap(matrix=matrix, dpi=dpi)
        page_im = Image.frombytes("RGB", (page_pix.width, page_pix.height), page_pix.samples)

        for i, block in enumerate(blocks[int(skip_block):]):  # head and tail of pages should be ignore
            if 'image' in block:
                # try:
                    bbox = block['bbox']
                    # skip image that width=398 and hight=137 -> Typically LOGO
                    if (bbox[2] - bbox[0])*scale - LOGO_WIDTH <= 10 and (bbox[3] - bbox[1])*scale - LOGO_HEIGHT <= 10:
                        continue
                    # Scale the bbox coordinates
                    cropped = page_im.crop([int(i * scale) for i in bbox])
                    number = block['number']

                    file_name = temp_image_dir + f'/image_{page.number}_{number}'
                    image_name = file_name + '.png'
                    # print(image_name)
                    cropped.save(image_name)
                    # # Handle text extraction around the image
                    text_content = get_text_around_image(blocks[skip_block:], i, lang)
                    title = get_title_of_image(blocks[skip_block:], i, lang)
                    # print(text_content[:30])
                    # print(title)
                    with open(f'{file_name}.txt', 'w') as text_file:
                        text_file.write(title + '\n' + text_content.replace('\n', ' '))
                # except:
                #     pass
    return temp_image_dir


def build_index(file, tmp_dir, lang='CN'):
    # Define the schema for the index
    if lang=='CN':
        schema = Schema(file_name=ID(stored=True), content=TEXT(analyzer=ChineseAnalyzer(), stored=True))
    else:
        schema = Schema(file_name=ID(stored=True), content=TEXT(stored=True))

    # base_name = os.path.basename(file).split('.')[0]
    # path_name = f'{base_name}'
    # index_path = path_name + '_index_dir'
    # # Create an index in a directory
    # if os.path.exists(index_path):
    #     shutil.rmtree(index_path)
    # os.mkdir(index_path)
    temp_index_dir = tempfile.mkdtemp(prefix='index_')

    ix = create_in(temp_index_dir, schema)

    # Add documents to the index
    # base_name = os.path.basename(file).split('.')[0]
    # image_path = f'images{base_name}'
    writer = ix.writer()
    for file in os.listdir(tmp_dir):
        if file.endswith('.txt'):
            file_path = os.path.join(tmp_dir, file)
            with open(file_path, 'r') as f:
                content = f.read()
            writer.add_document(file_name=file[:-4], content=content)
            # print('==========')
            # print(content)
            # print("==========")

    writer.commit()
    return ix, temp_index_dir


def search(ix, query, lang='CN', k=10):

    # Tokenize the query string and join tokens with OR operator
    if lang == 'CN':
        query_tokens = jieba.cut(query, cut_all=True)
    else:
        query_tokens = query.split()
    or_query = " OR ".join(query_tokens)

    parser = QueryParser("content", ix.schema)
    myquery = parser.parse(or_query)

    with ix.searcher() as searcher:
        results = searcher.search(myquery, limit=k)

        # Extract and return the file names and descriptions of the top-k hits
        results_list = [(hit['file_name'], hit.highlights("content"), hit) for hit in results]

    return results_list


def return_image(file, results_list, tmp_dir):
    # base_name = os.path.basename(file).split('.')[0]
    # path_name = f'images{base_name}'
    titles = []
    images = []
    for result in results_list:
        title = result[2].fields()['content'].split('\n')[0].split(':')[1]
        titles.append(title)
        images.append(Image.open(tmp_dir + '/' + result[0] + '.png'))
    return titles[0], images[0]


# file = 'CA-IS372x-datasheet_cn.pdf'
# temp_image_dir = load_pdf(file, lang='CN')
# ix, temp_index_dir = build_index(file, temp_image_dir)
# results_list = search(ix, '波形', lang='CN', k=10)
# ret_img = return_image(file, results_list, temp_image_dir)
# print('title: ' + ret_img[0])
# ret_img[1].show()

