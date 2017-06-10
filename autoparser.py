from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs

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

def is_not_first_tag(xpath):
    return get_tag_with_number(xpath).replace(get_tag(xpath), '')

def xpath_sibling(xpath, num):
    tag_name = str(get_tag(xpath))
    xpath = str(xpath)
    xpath = '/'.join(xpath.split('/')[:-1]) + '/' + tag_name
    if num != 1:
         xpath += '[' + str(num) + ']'
    return xpath

def remove_nulls_map(attrs):
    attrs_new = {}
    for attr in attrs:
        if attrs[attr]:
            attrs_new[attr] = attrs[attr]
    return attrs_new

def all_attrs(xpath, attrs, driver):
    tag_number = int(re.sub('[^0-9]+', '', is_not_first_tag(xpath)))
    attrs = remove_nulls_map(attrs)
    len_attrs = len(attrs)
    for i in range(1, tag_number):
        xpath_cur = xpath_sibling(xpath, i)
        e = driver.find_element_by_xpath(xpath_cur)
        cnt = 0
        for attr in attrs:
            attr_val = attrs[attr]
            if attr_val != e.get_attribute(attr):
                continue
            cnt += 1
        if cnt == len_attrs:
            return xpath
    return attrs


def find_unique_selector(xpath, e, cls_big, driver):
    tag_number = int(re.sub('[^0-9]+', '', is_not_first_tag(xpath)))
    attrs = driver.execute_script(
        'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) '
        '{ items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
        e)
    for i in range(1, tag_number):
        xpath_cur = xpath_sibling(xpath, i)
        e = driver.find_element_by_xpath(xpath_cur)
        if e.get_attribute('class') == cls_big:
            return all_attrs(xpath, attrs, driver)


def remove_nulls(arr):
    ret_arr = []
    for a in arr:
        if a:
            ret_arr.append(a)
    return ret_arr

def find_most_common_regex(ids):
    reg_map = {}
    for i in ids:
        id_reg_filtered = re.sub("[0-9]", "", i)
        if id_reg_filtered not in reg_map:
            reg_map[id_reg_filtered] = 1
        else:
            reg_map[id_reg_filtered] += 1
    return sorted(reg_map, key=reg_map.get, reverse=True)[0]

def find_most_common_class(classes):
    cls_map = {}
    for cls in classes:
        if cls not in cls_map:
            cls_map[cls] = 1
        else:
            cls_map[cls] += 1
    cls_name = sorted(cls_map, key=cls_map.get, reverse=True)[0]
    if cls_name:
        return cls_name
    return False

def find_row_selector(ids, classes):
    ids = remove_nulls(ids)
    classes = remove_nulls(classes)
    id_regex = None
    cls_name = None
    if ids:
        id_regex = find_most_common_regex(ids)
    if classes:
        cls_name = find_most_common_class(classes)
    if id_regex:
        return str(id_regex) + '[0-9]+'
    elif cls_name:
        return str(cls_name)
    return False

def check_group_of_widths(same_width_elements):
    level_required = level_with_max_count(same_width_elements)
    same_width_elements_new = []
    total_height = 0
    index_big_element = 0
    cur_level = 0
    next_level = 0
    cur_height = 0
    next_height = 0
    skip = 1
    index = 0
    while index < len(same_width_elements)-1:
        cur_level = find_level(same_width_elements[index_big_element][0])
        next_level = find_level(same_width_elements[index_big_element+skip][0])
        cur_height = same_width_elements[index_big_element][1]
        next_height = same_width_elements[index_big_element+skip][1]
        if skip == 1:
            total_height += cur_height
            same_width_elements_new.append(same_width_elements[index_big_element])
        index += 1
        if cur_level > next_level and not (total_height > 0.9*next_height and total_height < next_height):
            skip += 1
            continue
        index_big_element += skip
        skip = 1
        if total_height > 0.9*next_height and total_height < next_height and cur_level > next_level:
            break
    if index != len(same_width_elements)-1:
        return same_width_elements[index], same_width_elements_new
    return False, False

def check_separated_group_of_widths(same_width_elements, parent):
    if parent[4] == 0:
        return False
    height = 0
    parent_height = parent[1]
    for elem in same_width_elements:
        height += elem[1]
    if height > 0.9*parent_height and height < 1.1*parent_height:
        return parent
    return False

def level_with_max_count(same_width_elements):
    level_map = create_level_map(same_width_elements)
    return sorted(level_map, key=level_map.get, reverse=True)[0]

def find_most_common_parent(same_width_elements):
    parents = ['/'.join(x[0].split('/')[:-1]) for x in same_width_elements]
    parent_map = {}
    for parent in parents:
        if parent not in parent_map:
            parent_map[parent] = 1
        else:
            parent_map[parent] += 1
    parent_xpath = sorted(parent_map, key=parent_map.get, reverse=True)[0]
    for elem in same_width_elements:
        if parent_xpath == elem[0]:
            return elem
    return parent_xpath

def get_tag_with_number(elem):
    return elem.split('/')[-1]

def get_tag(elem):
    return get_tag_with_number(elem).split('[')[0]

def find_elems_with_most_common_tag_name_or_parent(same_width_elements, name_or_parent=True):
    tag_map = {}
    for elem in same_width_elements:
        if name_or_parent:
            tag = get_tag(elem[0])
        else:
            xpath_parent = '/'.join(elem[0].split('/')[:-1])
            tag = get_tag_with_number(xpath_parent)
        if tag not in tag_map:
            tag_map[tag] = 1
        else:
            tag_map[tag] += 1
    common_tag = sorted(tag_map, key=tag_map.get, reverse=True)[0]
    same_width_elements_new = []
    for elem in same_width_elements:
        if name_or_parent:
            tag = get_tag(elem[0])
        else:
            xpath_parent = '/'.join(elem[0].split('/')[:-1])
            tag = get_tag_with_number(xpath_parent)
        if tag == common_tag:
            same_width_elements_new.append(elem)
    return same_width_elements_new

def get_common_parent_size(same_width_elements, most_common_parent):
    for elem in same_width_elements:
        if elem[0] == most_common_parent:
            return elem

def filter_by_parent(same_width_elements, parent):
    same_width_elements_new = []
    for elem in same_width_elements:
        if parent in elem[0]:
            same_width_elements_new.append(elem)
    return same_width_elements_new

def find_elems_with_most_common_immediate_parent(same_width_elements):
    same_width_elements = find_elems_with_most_common_tag_name_or_parent(same_width_elements, False)
    if len(same_width_elements) < min_posts:
        return same_width_elements, False
    return same_width_elements, True


def level_with_max_number_of_elems_with_same_parent(same_width_elements, sizes):
    level_map = create_level_map(same_width_elements)
    levels = sorted([key for key in level_map])
    for level in levels:
        if level_map[level] < min_posts:
            continue
        else:
            same_width_elements_new = []
            for elem in same_width_elements:
                if find_level(elem[0]) == level:
                    same_width_elements_new.append(elem)
            same_width_elements_new = list(set(same_width_elements_new))
            same_width_elements_new.sort(key=lambda x: x[4])
            same_width_elements_new = find_elems_with_most_common_tag_name_or_parent(same_width_elements_new)
            if len(same_width_elements_new) < min_posts:
                continue
            same_width_elements_new, success = find_elems_with_most_common_immediate_parent(same_width_elements_new)
            if success:
                most_common_parent = find_most_common_parent(same_width_elements_new)
                same_width_elements_new = filter_by_parent(same_width_elements_new, most_common_parent)
                most_common_parent_size = get_common_parent_size(sizes, most_common_parent)
                same_width_elements_new.sort(key = lambda x: x[4])
                return most_common_parent_size, same_width_elements_new
            else:
                continue
    return False, same_width_elements


def level_with_max_count_and_same_parent(same_width_elements):
    level_required = level_with_max_count(same_width_elements)
    same_width_elements_new = []
    for elem in same_width_elements:
        level = find_level(elem[0])
        if level == level_required:
            same_width_elements_new.append(elem)
    same_width_elements_new = find_elems_with_most_common_tag_name_or_parent(same_width_elements_new)
    most_common_parent = find_most_common_parent(same_width_elements_new)
    same_width_elements_new = filter_by_parent(same_width_elements_new, most_common_parent)
    most_common_parent_size = get_common_parent_size(same_width_elements, most_common_parent)
    same_width_elements_new.sort(key = lambda x: x[4])
    return most_common_parent_size, same_width_elements_new

def create_level_map(same_width_elements):
    level_map = {}
    for elem in same_width_elements:
        level = find_level(elem[0])
        if level not in level_map:
            level_map[level] = 0
        else:
            level_map[level] += 1
    return level_map

def get_same_width_elements(sizes, max_width_key):
    same_width_elements = []
    for size in sizes:
        if size[2] == max_width_key:
            # print size
            same_width_elements.append(size)
    same_width_elements = list(set(same_width_elements))
    same_width_elements.sort(key = lambda x: (x[1], -find_level(x[0])))
    return same_width_elements

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

def are_neighbors(width, size):
    diff = abs(width - size)
    return diff < 5 and diff != 0

def quantize_widths(sizes, top_5_widths):
    for width in top_5_widths:
        for i in range(len(sizes)):
            size = sizes[i]
            if are_neighbors(width, size[2]):
                sizes[i] = size[0:2] + (width,) + size[3:]
    return sizes


print "Initiating Firefox"
driver = webdriver.Firefox()
# driver = webdriver.PhantomJS()
print "done"

# driver.get("file:///home/manji369/Downloads/Python_Scripts/seleniumScripts/test_page.html")
# driver.get("https://stackoverflow.com/questions/40471/differences-between-hashmap-and-hashtable")
# driver.get("https://stackoverflow.com/questions/14816166/rotate-camera-preview-to-portrait-android-opencv-camera")
driver.get(url)
# driver.get("file:///" + home_path + "1401.htm")

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
                '/noscript',
                '/fieldset',
                '/select',
                '/option'
                ]

xpaths = []
for child in children:
    xpath = xpath_soup(child)
    for replacement in replacements:
        xpath = xpath.replace(replacement, '')
    xpaths.append(xpath)

sizes = []
couldnot_find = 0
f = open(home_path + 'xpaths.txt', 'w')
print 'Getting sizes of all elements....'
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

top_5_widths = top_5(width_map)
sizes = quantize_widths(sizes, top_5_widths)
top_5_widths.sort(reverse=True)
for max_width_key in top_5_widths:
    same_width_elements = get_same_width_elements(sizes, max_width_key)
    if len(same_width_elements) < min_posts:
        continue
    # big_element, same_width_elements = level_with_max_count_and_same_parent(same_width_elements)
    big_element, same_width_elements = level_with_max_number_of_elems_with_same_parent(same_width_elements, sizes)
    if len(same_width_elements) < min_posts:
        continue
    # big_element, same_width_elements = check_group_of_widths(same_width_elements)
    if big_element:
        big_element = check_separated_group_of_widths(same_width_elements, big_element)
    if big_element:
        break

# max_width = 0; max_width_key
# for key in width_map:
#     if width_map[key] > max_width:
#         max_width = width_map[key]
#         max_width_key = key
#
# print max_width_key

# print index_big_element
# if index_big_element == len(same_width_elements)-1:
#     new_max_width_key = -1; max_width = 0
#     for key in width_map:
#         if width_map[key] > max_width and key > max_width_key:
#             max_width = width_map[key]
#             new_max_width_key = key
#
# print new_max_width_key

same_width_elements.sort(key = lambda x: x[4])
print "Total " + str(len(same_width_elements)) + " posts found"
for elem in same_width_elements:
    print elem

big_element = big_element[0]
print "Main enclosing element xpath:" + big_element
e = driver.find_element_by_xpath(big_element)
highlight(e)
id_big = e.get_attribute('id')
cls_big = e.get_attribute('class')
tag_big = get_tag(big_element)
if not id_big:
    if is_not_first_tag(big_element):
        cls_big = find_unique_selector(big_element, e, cls_big, driver)

for elem in same_width_elements:
    e = driver.find_element_by_xpath(elem[0])
    highlight(e)

ids = []
classes = []
for elem in same_width_elements:
    e = driver.find_element_by_xpath(elem[0])
    ids.append(e.get_attribute('id'))
    classes.append(e.get_attribute('class'))

if id_big:
    print "Main css selector: " + str(tag_big) + "." + str(id_big)
elif cls_big:
    print "Main css selector: " + str(tag_big) + "." + str(cls_big)
else:
    print "Main xpath: " + str(big_element)

row_selector = find_row_selector(ids, classes)
if row_selector:
    print "Row css selector regex: " + str(get_tag(elem[0])) + '.' +str(row_selector)
else:
    print "Row tag:" + str(get_tag(elem[0]))