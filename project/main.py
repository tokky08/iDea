from flask import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random
import secret
import requests
from bs4 import BeautifulSoup

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

    print("wiki")

    try:
        ul = relation[0].ul
        li = ul.find_all("li")
        index = int(random.random()%len(li) - 1)
        result = li[index].string
        
        # 過去の連想ワードとの重複チェック
        for i in range(len(li) - 1):
            result = duplication(result, words_log, li, i)

        for word_log in words_log:
            if result == word_log:
                result = google(word, words_log)
                
    except IndexError:
        print("IndexError")
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

        # 過去の連想ワードとの重複チェック
        for i in range(len(elems) - 1):
            result = duplication(result, words_log, elems, i)
            
        for word_log in words_log:
            if result == word_log:
                result = "Give Up"

    except IndexError:
        result = elems[-1].string
        for word_log in words_log:
            if result == word_log:
                result = "Give Up IndexError"
    
    except ZeroDivisionError:
        result = "Give Up ZeroDivisionError"

    return result

def duplication(result, words_log, li, i):
    for word_log in words_log:
        if result == word_log:
            result = li[i].string
            print("befor:{}".format(result))


            for j in range(i, len(li)-1):
                result = not_ng_words(result, li, j)


            # ng_word_list = ng_words()
            # # print(ng_word_list)
            # for ng_word in ng_word_list:
            #     # print(ng_word)
            #     if ng_word in result:
            #         # print("test")
            #         i = i + 1
            #         result = li[i].string
            #         print("after:i:{},{}".format(i,result))
                    



            duplication(result, words_log, li, i + 1)
        
        else:
            for j in range(i, len(li)-1):
                result = not_ng_words(result, li, j)
            
    return result
    


def ng_words():
    path = "NG_word.txt"
    with open(path) as f:
        l_strip = [s.strip() for s in f.readlines()]
    
    return l_strip

def not_ng_words(result, li, i):
    ng_word_list = ng_words()
    for ng_word in ng_word_list:
        if ng_word in result:
            i = i + 1
            result = li[i].string
            not_ng_words(result, li, i+1)
            print("after:i:{},{}".format(i,result))
            return result
    return result
                


    


if __name__ == "__main__":
    app.run(debug=True)