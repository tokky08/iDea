from flask import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random
from flask import Flask, session, redirect, url_for,  request


app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
logs_user = {}

@app.route("/", methods=["GET", "POST"])
def top():
    if request.method == "GET":
        return render_template('top.html')
    else:
        word = scrayping(request.form["word"])
        log = []
        log.append(request.form["word"])
        log.append(word)
        session['id'] = random.random()
        session_id = session["id"]
        logs_user[session_id] = log

        # words_log = []
        # for id in logs_user:
        #     if str(id) == str(session_id):
        #         words_log = logs_user[id]

        # logs_user_func(session_id, word)
        words_log = words_log_func(session_id)


        return render_template('again.html', word=word, session_id=session_id, words_log=words_log)
        
@app.route("/again", methods=["GET", "POST"])
def again():
    session_id = request.form["session_id"]
    word = scrayping(request.form["word"])

    # words_log = []
    # for id in logs_user:
    #     if str(id) == str(session_id):
    #         logs_user[id].append(word)
    #         words_log = logs_user[id]

    logs_user_func(session_id, word)
    words_log = words_log_func(session_id)

    # logs.append(word)
    return render_template('again.html', word=word, session_id=session_id, words_log=words_log)

@app.route("/log", methods=["GET", "POST"])
def log():
    session_id = request.form["session_id"]

    # words_log = []
    # for id in logs_user:
    #     if str(id) == str(session_id):
    #         words_log = logs_user[id]
    
    words_log = words_log_func(session_id)

    return render_template('log.html', words_log=words_log)


def words_log_func(session_id):
    words_log = []
    for id in logs_user:
        if str(id) == str(session_id):
            words_log = logs_user[id]
    return words_log


def logs_user_func(session_id, word):
    for id in logs_user:
        if str(id) == str(session_id):
            logs_user[id].append(word)
    

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


## おまじない
if __name__ == "__main__":
    app.run(debug=True, threaded=True)