from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs

import itertools
import time

# def check_correct_bunch():


def top_5(width_map):
    return sorted(width_map, key=width_map.get, reverse=True)[:5]

def find_level(xpath):
    return xpath.count('/')

def highlight(element):
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].scrollIntoView(true);", element);
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                              element, s)
    original_style = element.get_attribute('style')
    apply_style("background: yellow; border: 2px solid red;")
    time.sleep(.3)
    apply_style(original_style)

def xpath_soup(element):
    """
    Generate xpath of soup element
    :param element: bs4 text or node
    :return: xpath as string
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        previous = itertools.islice(parent.children, 0, parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

print "Initiating Firefox"
driver = webdriver.Firefox()
# driver = webdriver.PhantomJS()
print "done"

# driver.get("file:///home/manji369/Downloads/Python_Scripts/seleniumScripts/test_page.html")
driver.get("https://stackoverflow.com/questions/40471/differences-between-hashmap-and-hashtable")
page_content = driver.page_source
soup = bs(page_content, "html.parser")

html = soup.find('html')
children = html.findChildren()
def find_element(xpath, driver):
    # xpath = xpath_soup(html)
    # print "xpath:", xpath
    try:
        e = driver.find_element_by_xpath(xpath)
    except:
        return -1, -1
    location = e.location
    size = e.size
    return location, size

replacements = [
                '/img',
                '/br',
                '/label',
                '/meta',
                '/link',
                '/input',
                '/svg',
                '/path',
                '/noscript'
                ]

xpaths = []
for child in children:
    xpath = xpath_soup(child)
    for replacement in replacements:
        xpath = xpath.replace(replacement, '')
    xpaths.append(xpath)

sizes = []
couldnot_find = 0
f = open('/home/manji369/xpaths.txt', 'w')
for i in range(len(xpaths)):
    xpath = xpaths[i]
    p = i*100/len(xpaths)
    print 'Progress [%d%%]\r'%p,
    location, size = find_element(xpath, driver)
    if location == -1:
        couldnot_find += 1
        f.write(xpath + '\n')
        continue
    if size['width'] > 200 and size['height'] > 100:
        sizes.append((xpath, size['height'], size['width'], location['x'], location['y']))
        # print xpath

f.close()
print "Could not find:", couldnot_find
sizes.sort(key = lambda x: x[1])

width_map = {}
for size in sizes:
    if size[2] not in width_map:
        width_map[size[2]] = 1;
    else:
        width_map[size[2]] += 1;

max_width = 0; max_width_key
for key in width_map:
    if width_map[key] > max_width:
        max_width = width_map[key]
        max_width_key = key

print max_width_key


same_width_elements = []
for size in sizes:
    if size[2] == max_width_key:
        print size
        same_width_elements.append(size)

same_width_elements.sort(key = lambda x: (x[1], -find_level(x[0])))

total_height = 0
index_big_element = 0
cur_level = 0
next_level = 0
cur_height = 0
next_height = 0
while index_big_element < len(same_width_elements)-1:
    cur_level = find_level(same_width_elements[index_big_element][0])
    next_level = find_level(same_width_elements[index_big_element+1][0])
    cur_height = same_width_elements[index_big_element][1]
    next_height = same_width_elements[index_big_element+1][1]
    total_height += cur_height
    index_big_element += 1
    if total_height > 0.9*next_height and total_height < next_height and cur_level > next_level:
        break

# print index_big_element
# if index_big_element == len(same_width_elements)-1:
#     new_max_width_key = -1; max_width = 0
#     for key in width_map:
#         if width_map[key] > max_width and key > max_width_key:
#             max_width = width_map[key]
#             new_max_width_key = key
#
# print new_max_width_key

for elem in same_width_elements:
    print elem

elem = same_width_elements[index_big_element]
print elem[0]
highlight(driver.find_element_by_xpath(elem[0]))
for i in range(index_big_element):
    elem = same_width_elements[i]
    e = driver.find_element_by_xpath(elem[0])
    highlight(e)
