from flask import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random



app = Flask(__name__)

logs = []

@app.route("/", methods=["GET", "POST"])
def top():
    if request.method == "GET":
        global logs
        logs = []
        return render_template('top.html')
    else:
        word = scrayping(request.form["word"])
        logs.append(request.form["word"])
        logs.append(word)
        return render_template('again.html', word=word, logs=logs)
        
@app.route("/again", methods=["GET", "POST"])
def again():
    # word = scrayping(request.form["word"])
    word = "グーグル"
    logs.append(word)
    return render_template('again.html', word=word, logs=logs)

@app.route("/log", methods=["GET", "POST"])
def log():
    return render_template('log.html', logs=logs)
        

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
    app.run(debug=True)