from flask import Flask
app = Flask(__name__)

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def scrayping():
    driver = webdriver.Chrome("driver/chromedriver")

    time.sleep(1)

    driver.get("https://www.google.co.jp")

    value = input()

    # 検索窓にSeleniumと入力する
    selector = '#tsf > div:nth-child(2) > div.A8SBwf > div.RNNXgb > div > div.a4bIc > input'
    element = driver.find_element_by_css_selector(selector)
    element.send_keys(value)

    # enterキーを押す
    element.send_keys(Keys.ENTER)

    element = driver.find_element_by_id("brs")
    element = driver.find_element_by_class_name("card-section")
    elements = element.text

    # print(elements)

    # for text in elements:
    #     if not text == value:
    #         print(text)
            
    driver.quit()

    return elements

@app.route('/')
def hello():
    name = scrayping()
    # name = "Hello World"
    return name

@app.route('/good')
def good():
    name = "Good"
    return name

## おまじない
if __name__ == "__main__":
    app.run(debug=True)