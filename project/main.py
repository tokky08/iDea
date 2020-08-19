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
        words_log = words_log_func(session_id)
        word = wikipedia(request.form["word"], words_log)
        log = []
        log.append(request.form["word"])
        log.append(word)
        # session['id'] = random.random()
        # session_id = session["id"]
        users_log[session_id] = log
        words_log = words_log_func(session_id)

        return render_template('again.html', word=word, session_id=session_id, words_log=words_log)
        
@app.route("/again", methods=["GET", "POST"])
def again():
    session_id = request.form["session_id"]
    words_log = words_log_func(session_id)
    # word = scrayping(request.form["word"])
    word = wikipedia(request.form["word"], words_log)
    users_log_func(session_id, word)
    # words_log = words_log_func(session_id)

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
        result = li[0].string

        # for word_log in words_log:
        #     if result == word_log:
        #         result = li[-1].string
        #     else:

        #         for item in words_log:
        #             if result == item:
        #                 result = li[-2].string



        if result == word:
            result = li[-1].string
            if result == word:
                result = google(word, words_log)
                
    except IndexError:
        # result = "ヒットしませんでした"
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

    print(words_log)
        
    try:
        index = int(random.random()%len(elems) - 1)
        result = elems[index].string
        if len(result.split(" "))>1:
            if result.split(" ")[0] == word:
                result = result.split(" ")[1]
            else:
                result = result.split(" ")[0]
        if result == "関連キーワード" or result== word:
            result = elems[index-1].string
            if len(result.split(" "))>1:
                if result.split(" ")[0] == word:
                    result = result.split(" ")[1]
                else:
                    result = result.split(" ")[0]
    except IndexError:
        result = elems[-1].string
        if result == "関連キーワード":
            result = elems[-2].string

    return result


if __name__ == "__main__":
    app.run(debug=True)