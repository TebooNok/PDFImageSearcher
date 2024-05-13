import jieba
from whoosh.qparser import QueryParser
from PIL import Image
from whoosh.index import open_dir
from whoosh.analysis import Tokenizer, Token


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


def search(query, lang='CN', k=10):

    ix = open_dir('indexes')
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
        results_list = [(hit['file_name'], hit['content'], hit.score) for hit in results]

        images = []
        for result in results_list:
            print(result)
            image_name = result[0]
            base_name = image_name.split('_img')[0]
            image_full_path = 'images/' + base_name + '/' + image_name + '.png' # 这个代码就是构造图片路径的
            img = Image.open(image_full_path)
            image_title = result[1].split('\n')[-1].split(':')[1]
            # img.show(title=image_title)
            images.append((img, image_title, result[2]))

        return images


jieba.cut("") # 用于预加载中文分词词典，建议提前运行这段命令
# results = search("IF-428x接收端阈值")
results = search("简化结构图")
for result in results:
    print(result[1], result[2]) # result[0] 是图片的 PIL.Image 对象， result[1]是title，2是相似度打分