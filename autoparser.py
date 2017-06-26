from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
from collections import Counter
from getPosts import *

import itertools
import time
import re
import sys


home_path = '/home/manji369/Downloads/Python_Scripts/seleniumScripts/Autoparser_Forums/Autoparser_pages/'
# home_path = '/home/revanth/Autoparser_Forums/Autoparser_pages/'
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
text_parent_ignore_list = ['p', 'li', 'strong']


print "Initiating Firefox"
driver = webdriver.Firefox()
# driver = webdriver.PhantomJS()
print "done"

driver.get(url)

""" Read the page with BeautifulSoup """
page_content = driver.page_source
soup = bs(page_content, "html.parser")

main_selector_soup, row_selector_soup = find_posts(soup, driver, home_path)
print "main_selector_soup", main_selector_soup
print "row_selector_soup", row_selector_soup
