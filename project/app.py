from flask import *
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import time
import random
import secret
import requests
from bs4 import BeautifulSoup
import re
import MeCab
import mecabpr
import pandas as pd
import unicodedata
from gensim.models import word2vec
# from functions import *

app = Flask(__name__)

app.secret_key = secret.secret_key
users_log = {}

@app.route("/", methods=["GET", "POST"])
def top():
    if request.method == "GET":
        return render_template('top.html')
    else:
        session['id'] = random.random()
        session_id = session["id"]
        log = []
        log.append(request.form["word"])
        users_log[session_id] = log
        words_log = words_log_func(session_id)
        word = wikipedia(request.form["word"], words_log)
        log.append(word)
        users_log[session_id] = log

        return render_template('again.html', word=word, session_id=session_id, words_log=words_log)
        
@app.route("/again", methods=["GET", "POST"])
def again():
    session_id = request.form["session_id"]
    words_log = words_log_func(session_id)
    word = wikipedia(request.form["word"], words_log)
    users_log_func(session_id, word)

    return render_template('again.html', word=word, session_id=session_id, words_log=words_log)

@app.route("/detail", methods=["GET", "POST"])
def detail():
    session_id = request.form["session_id"]
    words_log = words_log_func(session_id)
    word = request.form["word"]
    detail_text = wiki_detail(word)["text"]
    detail_url = wiki_detail(word)["url"]

    return render_template('detail.html', word=word, detail_text=detail_text, detail_url=detail_url, session_id=session_id, words_log=words_log)

@app.route("/log", methods=["GET", "POST"])
def log():
    session_id = request.form["session_id"]
    words_log = words_log_func(session_id)

    return render_template('log.html', words_log=words_log)


def words_log_func(session_id):
    words_log = []
    for id in users_log:
        if str(id) == str(session_id):
            words_log = users_log[id]
    return words_log


def users_log_func(session_id, word):
    for id in users_log:
        if str(id) == str(session_id):
            users_log[id].append(word)
    

def scrayping(word):
    driver = webdriver.Chrome("driver/chromedriver")

    time.sleep(1)

    driver.get("https://www.google.co.jp")

    # 検索窓にSeleniumと入力する
    selector = '#tsf > div:nth-child(2) > div.A8SBwf > div.RNNXgb > div > div.a4bIc > input'
    element = driver.find_element_by_css_selector(selector)
    element.send_keys(word)

    # enterキーを押す
    element.send_keys(Keys.ENTER)

    element = driver.find_element_by_id("brs")
    element = driver.find_element_by_class_name("card-section")
    elements = element.text
    elements = elements.split()
    elements = [text for text in elements if not text == word]
    
    result = random.choice(elements)
            
    driver.quit()

    return result

def wikipedia(word, words_log):
    res = requests.get('https://ja.wikipedia.org/wiki/' + word)
    soup = BeautifulSoup(res.text, 'html.parser')
    elems = soup.find(class_="ext-related-articles-card-list")
    relation = soup.find_all("div",id="mw-normal-catlinks")

    try:
        ul = relation[0].ul
        li = ul.find_all("li")
        index = int(random.random()%len(li) - 1)
        result = li[index].string

        # 重複チェックとNGワードチェックとスペースチェック
        for item in li:
            dupl = duplication_check(result, words_log)
            ng = ng_words_check(result)
            space = space_check(result)
            if dupl or ng or space:
                result = item.string
            else:
                break

        # 最後の重複チェックとNGワードチェックとスペースチェック
        dupl = duplication_check(result, words_log)
        ng = ng_words_check(result)
        space = space_check(result)
        if dupl or ng or space:
            result = google(word, words_log)
        
    except IndexError:
        result = google(word, words_log)
    
    return result


def google(word, words_log):
    res = requests.get('https://www.google.com/search?q=' + word)
    soup = BeautifulSoup(res.text, 'html.parser')
    elems = soup.find_all("span")
    elems = soup.find_all(class_="BNeawe deIvCb AP7Wnd")
        
    try:
        index = int(random.random()%len(elems) - 1)
        result = elems[index].string

        # 重複チェックとNGワードチェックとスペースチェック
        for item in elems:
            dupl = duplication_check(result, words_log)
            ng = ng_words_check(result)
            space = space_check(result)
            if dupl or ng or space:
                result = item.string
            else:
                break

        # 最後の重複チェックとNGワードチェックとスペースチェック
        dupl = duplication_check(result, words_log)
        ng = ng_words_check(result)
        space = space_check(result)
        if dupl or ng or space:
            result = all_google_wiki(word, words_log)

        return result

    except IndexError:
        result = elems[-1].string
        for word_log in words_log:
            if result == word_log:
                result = all_google_wiki(word, words_log)

        return result
    
    except ZeroDivisionError:
        result = all_google_wiki(word, words_log)

        return result


def duplication_check(result, words_log):
    for word_log in words_log:
        if result == word_log:
            return True    
    return False

def ng_words():
    path = "NG_word.txt"
    with open(path) as f:
        l_strip = [s.strip() for s in f.readlines()]
    return l_strip

def ng_words_check(result):
    ng_word_list = ng_words()
    for ng_word in ng_word_list:
        if re.search(ng_word, str(result)):
            return True
    return False

def space_check(result):
    result_list = str(result).split(" ")
    if len(result_list) > 1:
        english = english_check(result_list)
        return english
    return False

def english_check(result_list):
    check = re.compile('[a-zA-Zａ-ｚＡ-Ｚ]+')
    for item in result_list:
        if not check.fullmatch(item):
            return False
    return True



def all_google_wiki(word, words_log):
    preprocessing('https://www.google.com/search?q=', word)
    preprocessing('https://ja.wikipedia.org/wiki/', word)
    mecab(word)
    # result_list = word2vec_(word)
    result = word2vec_func(word, words_log)

    return result


def preprocessing(url, word):
    res = requests.get(url + word)
    soup = BeautifulSoup(res.text, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    lines = [line.strip() for line in text.splitlines()]

    with open('public_text.tsv','a', encoding='utf-8') as f:
        for r in lines:
            try:
                f.write(normalize_text(r) + '\n')
            except:
                continue

def mecab(word):
    #データ　インポート
    df = pd.read_csv(open('public_text.tsv','rU'), sep='\t', names=['text'], encoding='utf-8',engine='c')
    text_lists = df['text'].unique().tolist()

    #分かち書き
    # mt = MeCab.Tagger("-Ochasen -d '/path/mecab-ipadic~") #自分がインストールした辞書を指定
    mt = MeCab.Tagger() #自分がインストールした辞書を指定

    with open('public_text.txt', 'w', encoding='utf-8') as f:
        for text in text_lists:
            tmp_lists = []
            text = unicodedata.normalize('NFKC',str(text))
    #         if 'まじ卍' in text:
    #             text = text.replace('まじ卍','マジ卍')
            if word in text:
                text_splited = text.split(word)
                for i, text in enumerate(text_splited):
                    node = mt.parseToNode(text)
                    while node:
                        if node.feature.startswith('名詞') or node.feature.startswith('形容詞'):
                            tmp_lists.append(node.surface)
                        node = node.next
                    if i != len(text_splited)-1:
                        tmp_lists.append(word)
            else:
                node = mt.parseToNode(text)
            while node:
                if node.feature.startswith('名詞') or node.feature.startswith('形容詞'):
                    tmp_lists.append(node.surface)
                node = node.next
            f.write(' '.join(tmp_lists) + '\n')

def word2vec_func(word, words_log):
    # sentences = word2vec.LineSentence('public_text_splited_google.txt')
    sentences = word2vec.LineSentence("public_text.txt")
    model = word2vec.Word2Vec(
        sentences,
        sg=1,         #0: CBOW, 1: skip-gram
        size=300,     # ベクトルの次元数
        window=5,    # 入力単語からの最大距離
        min_count=5,  # 単語の出現回数でフィルタリング
    )

    word = replace(word, "（株）")

    try:
        result_list = model.most_similar(positive=word, topn=30)
        result = result_list[0][0]

        # 重複チェックとNGワードチェックとスペースチェック
        for i in range(len(result_list)):
            dupl = duplication_check(result, words_log)
            ng = ng_words_check(result)
            space = space_check(result)
            if dupl or ng or space:
                result = result_list[i][0]
            else:
                break

        return result

    # ボキャブラリーにないのでwordを品詞分解
    except KeyError:
        mpr = mecabpr.MeCabPosRegex()
        result_list = mpr.findall(word, "名詞-一般")
        result = result_list[-1][0]

        # 重複チェックとNGワードチェックとスペースチェック
        for i in range(len(result_list)):
            dupl = duplication_check(result, words_log)
            ng = ng_words_check(result)
            space = space_check(result)
            if dupl or ng or space:
                result = result_list[i][0]
            else:
                break

        return result


    # return result_list

def normalize_text(text):
    text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    text = re.sub('RT', "", text)
    text = re.sub('お気に入り', "", text)
    text = re.sub('まとめ', "", text)
    text = re.sub(r'[!-~]', "", text)
    text = re.sub(r'[︰-＠]', "", text)
    text = re.sub('\u3000',"", text)
    text = re.sub('\t', "", text)
    text = re.sub('·', "", text)
    text = re.sub('›', "", text)
    text = re.sub('~', "", text)
    text = re.sub('-', "", text)
    text = re.sub('こと', "", text)
    text = re.sub('日', "", text)
    text = re.sub('時間', "", text)
    text = re.sub('全角', "", text)
    text = re.sub('英数字', "", text)
    text = re.sub('半角', "", text)
    text = re.sub('カナ', "", text)
    text = re.sub('ローマ', "", text)
    text = re.sub('ここ', "", text)
    text = re.sub('場合', "", text)
    text = re.sub('クリック', "", text)
    text = re.sub('すべて', "", text)
    text = re.sub('ニュース', "", text)
    text = text.strip()

    return text

def replace(word, key):
    word = re.sub(key, "", word)
    return word


def wiki_detail(word):
    try:
        res = requests.get("https://ja.m.wikipedia.org/wiki/" + word)
        soup = BeautifulSoup(res.text, 'html.parser')
        elems = soup.find(id="mf-section-0")
        text = elems.p.text
        result = {
            "text": text,
            "url": "https://ja.m.wikipedia.org/wiki/" + word
        }
        return result
    except AttributeError:
        result = {
            "text": "",
            "url": google_url(word)
        }
        return result


def google_url(word):      
    response = requests.get('https://www.google.co.jp/search?q=' + word + "とは")
    response.raise_for_status()
    bs = BeautifulSoup(response.text, "html.parser")
    element = bs.select("a")

    title_list = []
    url_list = []
    for i in range(len(element)):
        title = element[i].get_text()    
        url = element[i].get('href').replace('/url?q=','')
        title_list.append(title)
        url_list.append(url)
        
    title_list_02 = []
    url_list_02 = []
    for i in range(17, len(title_list)):
        title_list_02.append(title_list[i])
        url_list_02.append(url_list[i])
        
    title_list_03 = []
    url_list_03 = []
    for i in range(len(title_list_02)):
        if "https:" in url_list_02[i]:
            title_list_03.append(title_list_02[i])
            url_list_03.append(url_list_02[i])

    return url_list_03[0]



if __name__ == "__main__":
    app.run(debug=True)