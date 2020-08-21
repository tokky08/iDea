from flask import *
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import time
import random
import secret
import requests
from bs4 import BeautifulSoup
import re     

app = Flask(__name__)

app.secret_key = secret.secret_key
users_log = {}

@app.route("/", methods=["GET", "POST"])
def top():
    if request.method == "GET":
        return render_template('top.html')
    else:
        # word = scrayping(request.form["word"])
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
    # word = scrayping(request.form["word"])
    word = wikipedia(request.form["word"], words_log)
    users_log_func(session_id, word)

    return render_template('again.html', word=word, session_id=session_id, words_log=words_log)

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

    # スクレイピング対象の URL にリクエストを送り HTML を取得する
    res = requests.get('https://ja.wikipedia.org/wiki/' + word)

    # レスポンスの HTML から BeautifulSoup オブジェクトを作る
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
    # スクレイピング対象の URL にリクエストを送り HTML を取得する
    res = requests.get('https://www.google.com/search?q=' + word)

    # レスポンスの HTML から BeautifulSoup オブジェクトを作る
    soup = BeautifulSoup(res.text, 'html.parser')

    # elems = soup.find(class_="ext-related-articles-card-list")
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
            result = "ヒットしませんでした。現在開発中です。"

        return result

    except IndexError:
        result = elems[-1].string
        for word_log in words_log:
            if result == word_log:
                result = "IndexError"

        return result
    
    except ZeroDivisionError:
        result = "ZeroDivisionError"

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

# def space_select(result):
#     result_list = result.split(" ")
#     index = int(random.random() % len(result_list))
#     result_select = result_list[index]
#     if result_select == result:
#         if index == 0:
#             result_select = result_list[index + 1]
#         else:
#             result_select = result_list[index - 1]
#         return result_select
#     else:
#         return result_select


if __name__ == "__main__":
    app.run(debug=True)