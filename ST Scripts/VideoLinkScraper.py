#to install package from virtual env, cd to {virtualenv_path}/bin 
#then do ./python pip install 

import time, datetime

import urllib.request, urllib.error, urllib.parse

from selenium import webdriver
import subprocess

proc = subprocess.Popen('apt install chromium-chromedriver', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
proc.wait()

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.options import Options

# A Python Selenium Scraper for Retrieve the List of Links from A Channel
def yt_scrapper_link(url):
    channelid = url.split('/')[4]
    #driver=webdriver.Firefox()
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=chrome-data")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    driver.get(url)
    time.sleep(5)
    dt=datetime.datetime.now().strftime("%Y%m%d%H%M")
    height = driver.execute_script("return document.documentElement.scrollHeight")
    lastheight = 0

    while True:
        if lastheight == height:
            break
        lastheight = height
        driver.execute_script("window.scrollTo(0, " + str(height) + ");")
        time.sleep(2)
        height = driver.execute_script("return document.documentElement.scrollHeight")

    user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')
    
    print("The total number of videos catched is: {}".format(len(user_data)))

    for i in user_data:
        # print(i.get_attribute('href'))
        link = (i.get_attribute('href'))
        print(link)
        # f = open(channelid+'-'+dt+'.list', 'a+')
        # f.write(link + '\n')
    # f.close