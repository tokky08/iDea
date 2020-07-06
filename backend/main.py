from flask import Flask
from flask import render_template
from flask import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random



app = Flask(__name__)

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('index.html', name=name)


@app.route("/", methods=["GET", "POST"])
def odd_even():
    if request.method == "GET":
        return render_template('index.html')
    else:
        return scrayping(request.form["word"])

def scrayping(word):
    driver = webdriver.Chrome("driver/chromedriver")

    time.sleep(1)

    driver.get("https://www.google.co.jp")

    value = word

    # 検索窓にSeleniumと入力する
    selector = '#tsf > div:nth-child(2) > div.A8SBwf > div.RNNXgb > div > div.a4bIc > input'
    element = driver.find_element_by_css_selector(selector)
    element.send_keys(value)

    # enterキーを押す
    element.send_keys(Keys.ENTER)

    element = driver.find_element_by_id("brs")
    element = driver.find_element_by_class_name("card-section")
    elements = element.text
    elements = elements.split()
    elements = [text for text in elements if not text == value]
    
    result = random.choice(elements)
            
    driver.quit()

    return result


## おまじない
if __name__ == "__main__":
    app.run(debug=True)