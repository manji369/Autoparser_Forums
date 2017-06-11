from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
from values import *

import itertools
import time
import re
import sys


# home_path = '/home/manji369/Downloads/Python_Scripts/seleniumScripts/Autoparser_Forums/Autoparser_pages/'
home_path = '/home/revanth/Autoparser_Forums/Autoparser_pages/'
# url = "https://www.raspberrypi.org/forums/viewtopic.php?f=91&t=94424"
# url = "file:///home/manji369/Downloads/Python_Scripts/seleniumScripts/test_page.html"
# url = "https://stackoverflow.com/questions/40471/differences-between-hashmap-and-hashtable"
# url = "https://stackoverflow.com/questions/14816166/rotate-camera-preview-to-portrait-android-opencv-camera"
# url = "file:///" + home_path + "1401.htm"
# url = "file:///" + home_path + "alfursan.htm"
# url = "file:///" + home_path + "aoreteam.htm"
url = "file:///" + home_path + "audonjon.htm"
""" url = "file:///" + home_path + "abtalealdjazaire.htm" """
min_posts = 5

def get_rows_description(soup):
    posts = soup.find('div', {'id': 'brdmain'})
    rows = posts.find_all('div', {'id': re.compile('p[0-9]+')})
    return rows

driver = webdriver.Firefox()
# driver = webdriver.PhantomJS()
print "done"

driver.get(url)

""" Read the page with BeautifulSoup """
page_content = driver.page_source
soup = bs(page_content, "html.parser")
rows = get_rows_description(soup)
row = rows[0]
user_name = appendToUsers.strip()
user_tag = row.find(text=re.compile('user_name'))