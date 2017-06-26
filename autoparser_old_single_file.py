from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
from collections import Counter

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
url = "file:///" + home_path + "1401.htm"
# url = "file:///" + home_path + "alfursan.htm"
# url = "file:///" + home_path + "aoreteam.htm"
# url = "file:///" + home_path + "audonjon.htm"
""" url = "file:///" + home_path + "abtalealdjazaire.htm" """
min_posts = 5
text_parent_ignore_list = ['p', 'li', 'strong']

def is_not_first_tag(xpath):
    """
    Returns an empty string if the tag is the first tag with that tag name of a
    given parent. If it is not the first tag returns [tag_number] where tag_number
    is the occurence number of that tag
    """
    return get_tag_with_number(xpath).replace(get_tag(xpath), '')

def xpath_sibling(xpath, num):
    """
    Returns the xpath of a sibling element with same tag name as the given element
    and the occrence number being num.
    """
    tag_name = str(get_tag(xpath))
    xpath = str(xpath)
    xpath = '/'.join(xpath.split('/')[:-1]) + '/' + tag_name
    if num != 1:
         xpath += '[' + str(num) + ']'
    return xpath

def remove_nulls_map(attrs):
    """
    Removes nulls from a dictionary and returns everthing else
    """
    attrs_new = {}
    for attr in attrs:
        if attrs[attr]:
            attrs_new[attr] = attrs[attr]
    return attrs_new

def all_attrs(xpath, attrs, driver):
    """
    Helper function that returns all the attributes (dictionary of attributes
    and values) of a given element, if another other sibling element doesnot
    have exactly all the same values for attributes. If there is any sibling that
    has all the same attributes as given element it returns the xpath that is input
    to it.
    """
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
    """
    Checks if any of the sibling elements have same class as current element. If
    not returns the input class name
    """
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
    return cls_big


def remove_nulls(arr):
    """
    Removes all null elements from an array and returns it
    """
    ret_arr = []
    for a in arr:
        if a:
            ret_arr.append(a)
    return ret_arr

def find_most_common_regex(ids):
    """
    Finds the most common regex of all the ids of posts detected. This is to filter
    out small abberations which might be detected along with actual posts
    """
    reg_map = {}
    for i in ids:
        id_reg_filtered = re.sub("[0-9]", "", i)
        if id_reg_filtered not in reg_map:
            reg_map[id_reg_filtered] = 1
        else:
            reg_map[id_reg_filtered] += 1
    return sorted(reg_map, key=reg_map.get, reverse=True)[0]

def find_most_common_class(classes):
    """
    Returns the value of attribute class that is most common among the posts detected.
    Again this is to filter out small abberations which might be detected along
    with actual posts
    """
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
    """
    Master function for the two functions find_most_common_regex and
    find_most_common_class. Returns id_regex if it is present. If not looks for
    class name. If not returns false
    """
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
    """
    Old method. Not currently in use.
    """
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
    """
    Calculates the sum of heights of all the posts detected and checks if the
    height of main enclosing element is aprroximately same as the calculated one.
    """
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
    """
    Returns the level which has maximum number of elements from a group of same
    width elements
    """
    level_map = create_level_map(same_width_elements)
    return sorted(level_map, key=level_map.get, reverse=True)[0]

def find_most_common_parent(same_width_elements):
    """
    Given a group of same width elements, returns the parent that is most common.
    """
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
    """
    Given an xpath, returns the tag along with the occurence number of tag.
    eg. div[5]
    """
    return elem.split('/')[-1]

def get_tag(elem):
    """
    Given an xpath, returns the tag name of the element
    eg. div
    """
    return get_tag_with_number(elem).split('[')[0]

def find_elems_with_most_common_tag_name_or_parent(same_width_elements, name_or_parent=True):
    """
    Two modes:
    if name_or_parent is True:
        Given a list of same width elements, returns the elements with most common
        tag name
    else:
        Given a list of same width elements, returns the elements with most common
        parent
    """
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
    """
    Returns the size (length and width) of the required parent from the sizes
    grabbed earlier and grouped as same width elements
    """
    for elem in same_width_elements:
        if elem[0] == most_common_parent:
            return elem

def filter_by_parent(same_width_elements, parent):
    """
    Removes all elements that don't have the given tag name as parent
    """
    same_width_elements_new = []
    for elem in same_width_elements:
        if parent in elem[0]:
            same_width_elements_new.append(elem)
    return same_width_elements_new

def find_elems_with_most_common_immediate_parent(same_width_elements):
    """
    Master function for find_elems_with_most_common_tag_name_or_parent. Also Checks
    if number of posts detected are less than minimum number of posts.
    """
    same_width_elements = find_elems_with_most_common_tag_name_or_parent(same_width_elements, False)
    if len(same_width_elements) < min_posts:
        return same_width_elements, False
    return same_width_elements, True


def level_with_max_number_of_elems_with_same_parent(same_width_elements, sizes):
    """
    Master function for find_elems_with_most_common_immediate_parent and uses the
    returned elements from that function to find most common parent by calling
    find_most_common_parent and then filters the elements by that parent.
    """
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
    """
    Master function for find_elems_with_most_common_tag_name_or_parent,
    find_most_common_parent and returns a tuple containing parents xpath, size and
    location
    """
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
    """
    Returns a counter of the levels
    """
    level_map = {}
    for elem in same_width_elements:
        level = find_level(elem[0])
        if level not in level_map:
            level_map[level] = 0
        else:
            level_map[level] += 1
    return level_map

def get_same_width_elements(sizes, max_width_key):
    """
    Returns the elements with a given width (max_width_key)
    """
    same_width_elements = []
    for size in sizes:
        if size[2] == max_width_key:
            # print size
            same_width_elements.append(size)
    same_width_elements = list(set(same_width_elements))
    same_width_elements.sort(key = lambda x: (x[1], -find_level(x[0])))
    return same_width_elements

def top_5(width_map):
    """
    Finds 5 widths that have the most number of elements and sorts them by the width
    """
    return sorted(width_map, key=width_map.get, reverse=True)[:5]

def find_level(xpath):
    """
    Returns level of an element from xpath
    """
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
    time.sleep(.1)
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
    """
    Checks if two widths are less than 5 units apart.
    """
    diff = abs(width - size)
    return diff < 5 and diff != 0

def quantize_widths(sizes, top_5_widths):
    """
    Uses are_neighbors to quantize widths to top_5_widths.
    This is to filter out abberations where parent tag doesnot have the exact same
    width as posts
    """
    for width in top_5_widths:
        for i in range(len(sizes)):
            size = sizes[i]
            if are_neighbors(width, size[2]):
                sizes[i] = size[0:2] + (width,) + size[3:]
    return sizes

def find_element(xpath, driver):
    """
    Finds a given element in webpage opened using selenium via firefox from xpath
    and returns its location and size if its found. Else returns -1, -1
    """
    # xpath = xpath_soup(html)
    # print "xpath:", xpath
    try:
        e = driver.find_element_by_xpath(xpath)
    except:
        return -1, -1
    location = e.location
    size = e.size
    return location, size

print "Initiating Firefox"
driver = webdriver.Firefox()
# driver = webdriver.PhantomJS()
print "done"

driver.get(url)

""" Read the page with BeautifulSoup """
page_content = driver.page_source
soup = bs(page_content, "html.parser")

""" Find all the children tags """
html = soup.find('html')
children = html.findChildren()

""" Replacement tag names to be replaced """
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

"""
Convert each child soup object to xpath and replace all the replacements in all
the xpaths because selenium does not find these elements.
"""
xpaths = []
for child in children:
    xpath = xpath_soup(child)
    for replacement in replacements:
        xpath = xpath.replace(replacement, '')
    xpaths.append(xpath)


"""
Grab size (height, width) and location (x, y) of each element and store them in
a list sizes if the width > 200 and height > 100. Also write the xpaths that were
 not found by selenium to a file so that the replacements can be updated
"""
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

""" Close the file and print the number of elements that were not found """
f.close()
print "Could not find:", couldnot_find
""" Sort the sizes by height """
sizes.sort(key = lambda x: x[1])

""" Create a counter for widths """
width_map = {}
for size in sizes:
    if size[2] not in width_map:
        width_map[size[2]] = 1;
    else:
        width_map[size[2]] += 1;

""" Find the top 5 widths (by occurence) """
top_5_widths = top_5(width_map)
""" Quantize the widths and sort them by width """
sizes = quantize_widths(sizes, top_5_widths)
top_5_widths.sort(reverse=True)
"""
For each width check if the width is the required width.
"""
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

"""
Sort same width elements that were detected to be posts by y coordinate (order in
which they appear) and print them.
"""
same_width_elements.sort(key = lambda x: x[4])
print "Total " + str(len(same_width_elements)) + " posts found"
for elem in same_width_elements:
    print elem

""" Find the id and class name of parent and highlight the parent and posts detected
in browser.
"""
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

"""
Find the ids and class names of all the detected posts
"""
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


def remove_nulls_strings(contents):
    contents_new = []
    for content in contents:
        content_str = content.encode('utf-8')
        if content_str.strip():
            contents_new.append(content)
    return contents_new

def has_atleast_one_alphabet(text):
    if re.search('[a-zA-Z]', text):
        return True
    return False

def is_in_more_than_half(key, text_maps):
    len_maps = len(text_maps)
    key_cnt = 0
    for text_map in text_maps:
        if key in text_map:
            key_cnt += 1
    return key_cnt > len_maps/2

def filter_based_on_count(text_to_be_filtered):
    text_maps = [Counter(text) for text in text_to_be_filtered]
    text_map_overall = Counter(i for i in list(itertools.chain.from_iterable(text_to_be_filtered)))
    remove_these = set()
    for key in text_map_overall:
        if is_in_more_than_half(key, text_maps):
            remove_these.add(key)
    text_to_be_filtered_new = []
    for text_to_be_filtered_row in text_to_be_filtered:
        text_to_be_filtered_row_new = []
        for text in text_to_be_filtered_row:
            # if text not in remove_these and has_atleast_one_alphabet(text):
            if text not in remove_these:
                text_to_be_filtered_row_new.append(text)
        text_to_be_filtered_new.append(text_to_be_filtered_row_new)
    return text_to_be_filtered_new

def find_non_unique_attrs(attrs):
    unique_attr_keys = ['id', 'href']
    attrs_new = {}
    for key in attrs:
        if key not in unique_attr_keys:
            attrs_new[key] = attrs[key]
    return attrs_new

def find_3_parents(elem, row):
    parents_and_attrs = []
    parent_elem = elem
    i = 0
    while i < 3:
        parent_elem = parent_elem.parent
        if parent_elem == row:
            break
        if parent_elem.name not in text_parent_ignore_list:
            # attrs = find_non_unique_attrs(parent_elem.attrs)
            attrs = parent_elem.attrs
            parents_and_attrs = [(parent_elem.name, attrs)] + parents_and_attrs
            i += 1
    cur_elem = row
    prev_elem = row
    for parent, attrs in parents_and_attrs:
        if cur_elem:
            cur_elem = cur_elem.find(parent, attrs)
            if cur_elem:
                prev_elem = cur_elem
        else:
            cur_elem = prev_elem
            cur_elem = cur_elem.find(parent, attrs)
            if cur_elem:
                prev_elem = cur_elem
    if cur_elem.text == elem:
        return parents_and_attrs, False, False
    else:
        contents = cur_elem.contents
        for i in range(len(contents)):
            content = contents[i]
            if content == cur_elem:
                return parents_and_attrs, True, i
    return parents_and_attrs, False, False


def verify_parents_and_attrs(parents_and_attrs, row):
    parents_and_attrs_only, flag, cont_index = parents_and_attrs
    cur_elem = row
    prev_elem = row
    for parent, attrs in parents_and_attrs_only:
        if cur_elem:
            cur_elem = cur_elem.find(parent, attrs)
            if cur_elem:
                prev_elem = cur_elem
        else:
            cur_elem = prev_elem
            cur_elem = cur_elem.find(parent, attrs)
            if cur_elem:
                prev_elem = cur_elem
    if flag:
        cur_elem = cur_elem.contents[cont_index]
    else:
        cur_elem = cur_elem.text
    return cur_elem

def check_common_attrs_tag(parent_1, attrs_1, parent_2, attrs_2):
    if parent_1 != parent_2:
        return False
    else:
        if attrs_1 == attrs_2:
            return attrs_1
        else:
            if 'id' in attrs_1 and 'id' in attrs_2:
                id_1 = attrs_1.pop('id')
                id_2 = attrs_2.pop('id')
                if attrs_1 == attrs_2:
                    id_1 = re.sub('[0-9]+', '[0-9]+', id_1)
                    id_2 = re.sub('[0-9]+', '[0-9]+', id_2)
                    if id_1 == id_2:
                        attrs_1['id'] = id_1
                        return attrs_1
    return False

def find_common_attrs(parents_and_attrs_posts):
    parents_and_attrs_only = []
    [parents_and_attrs_post_1, parents_and_attrs_post_2] = parents_and_attrs_posts
    parents_and_attrs_only_1, flag_1, cont_ind_1 = parents_and_attrs_post_1
    parents_and_attrs_only_2, flag_2, cont_ind_2 = parents_and_attrs_post_2
    if len(parents_and_attrs_only_1) == len(parents_and_attrs_only_2):
        i = 0
        j_start = 0
        while i < len(parents_and_attrs_only_1):
            j = j_start
            while j < len(parents_and_attrs_only_2):
                parent_1, attrs_1 = parents_and_attrs_only_1[i]
                parent_2, attrs_2 = parents_and_attrs_only_2[j]
                regex_id = check_common_attrs_tag(parent_1, attrs_1, parent_2, attrs_2)
                if regex_id:
                    parents_and_attrs_only.append((parent_1, attrs_1))
                    j_start = j
                j += 1
            i += 1
    return parents_and_attrs_only, flag_1, cont_ind_1

# parents_and_attrs_only = []
# [parents_and_attrs_post_1, parents_and_attrs_post_2] = parents_and_attrs_posts
# parents_and_attrs_only_1, flag_1, cont_ind_1 = parents_and_attrs_post_1
# parents_and_attrs_only_2, flag_2, cont_ind_2 = parents_and_attrs_post_2
# if len(parents_and_attrs_only_1) == len(parents_and_attrs_only_2):
#     i = 0
#     j_start = 0
#     while i < len(parents_and_attrs_only_1):
#         j = j_start
#         while j < len(parents_and_attrs_only_2):
#             parent_1, attrs_1 = parents_and_attrs_only_1[i]
#             parent_2, attrs_2 = parents_and_attrs_only_2[j]
#             regex_id = check_common_attrs_tag(parent_1, attrs_1, parent_2, attrs_2)
#             if regex_id:
#                 parents_and_attrs_only.append((parent_1, attrs_1))
#                 j_start = j
#             i += 1
#             j += 1
# return parents_and_attrs_only, flag_1, cont_ind_1
#
# while i < len(parents_and_attrs_only_1):
#     j = j_start
#     while j < len(parents_and_attrs_only_2):
#         parent_1, attrs_1 = parents_and_attrs_only_1[i]
#         parent_2, attrs_2 = parents_and_attrs_only_2[j]
#         regex_id = check_common_attrs_tag(parent_1, attrs_1, parent_2, attrs_2)
#         if regex_id:
#             parents_and_attrs_only.append((parent_1, attrs_1))
#             j_start = j
#         i += 1
#         j += 1

def verify_parents_and_attrs_for_all_posts(parents_and_attrs, rows, text_filtered):
    for i, row in enumerate(rows):
        try:
            text_of_elem = verify_parents_and_attrs(parents_and_attrs, row)
            if text_of_elem.strip() not in text_to_be_filtered[i]:
                return False, i
        except:
            return False, i
    return True, -1

def find_post(text_row):
    initial_parent = False
    text_row.sort(key=lambda x: len(x), reverse=True)
    initial_parent = text_row[0].parent
    if initial_parent.name in text_parent_ignore_list:
        initial_parent = initial_parent.parent
    for text in text_row:
        text_parent = text.parent
        if text_parent.name in text_parent_ignore_list:
            text_parent = text_parent.parent
        if text_parent != initial_parent:
            break
    return initial_parent

def find_regex_attrs(parent):
    tag_name = parent.name
    attrs = parent.attrs
    for key in attrs:
        val = attrs[key][0]
        val = re.sub('[0-9]+', '[0-9]+', val)
        attrs[key] = val
    return  tag_name, attrs


# posts = soup.find('div', {'id': 'brdmain'})
# rows = posts.find_all('div', {'id': re.compile('p[0-9]+')})
# posts = soup.find('div', {'id': 'posts'})
# rows = posts.find_all('div', {'align': 'center'}, recursive=False)
posts = soup.find('div', {'id': 'postlist'})
rows = posts.find_all('div', {'id': re.compile('post_[0-9]+')}, recursive=False)
text_to_be_filtered = []
all_texts = []
for i in range(len(rows)):
    row = rows[i]
    text_row = remove_nulls_strings(row.find_all(text=re.compile('')))
    all_texts.append(text_row)
    # print "Post number ", i+1, ":"
    text_to_be_filtered_row = []
    for text in text_row:
        text_unicode = text.strip()
        if len(text_unicode) <= 20 and text.parent.name not in text_parent_ignore_list:
            text_to_be_filtered_row.append(text)
    text_to_be_filtered.append(text_to_be_filtered_row)


text_filtered = filter_based_on_count(text_to_be_filtered)
parents_and_attrs_posts = []
for i in range(2):
    print "Post number ", i+1, ":"
    post = text_filtered[i]
    row = rows[i]
    for i, text in enumerate(post):
        print str(i) + ':' + text
    print '\n'
    print "Enter index for user_name:"
    index = int(raw_input())
    parents_and_attrs = find_3_parents(post[index], row)
    parents_and_attrs_posts.append(parents_and_attrs)

parents_and_common_attrs = find_common_attrs(parents_and_attrs_posts)
if verify_parents_and_attrs_for_all_posts(parents_and_common_attrs, rows, text_filtered)[0]:
    print "Soup for user:", parents_and_common_attrs
    print "\nUsers found in given page:"
    for row in rows:
        print verify_parents_and_attrs(parents_and_common_attrs, row)
else:
    print "Failed to fetch soup for user"

print "\nInsert the index of post which has more text"
index = int(raw_input())
parent = find_post(all_texts[index])
if parent:
    parent = find_regex_attrs(parent)
    print "Soup for posts is:", parent
    print '\n Posts found in this page are:'
    parent_name = parent[0]
    parent_attrs = parent[1]
    for i, row in enumerate(rows):
        print "Post Number:", i+1
        print row.find(parent_name, parent_attrs).text
else:
    print "Failed to fetch soup for post"
