# Semi-Autoparser for Forums

##Finding the html elements that enclose the entire post (including memeber panel).

Forums have a specific structure for the description pages, the width of all the
posts being the same. Which means we can find all such html elements with the
same width and find the common parent. We can verify if the currently grabbed
posts are the correct ones by summing up the heights of all these elements and
matching this sum with the height of the parent element.

**Algorithm/Overview of method**

1. Input a page with a minimum number of 5 posts to the autoparser.
2. Open the page with firefox using selenium.
3. Find all the elements using BeautifulSoup.
4. Convert the soup objects to xpaths.
5. Locate each of these elements using selenium's find_element_by_xpath
6. Grab the size and location attributes of the selenium webdriver element found
    using step 5 and save them if the size is above a threshold value.
7. Create a map or counter of the widths obtained (containing the count of each widths).
8. Find the top_5_widths (based on the count) and sort them by value of width in
    descending order.
9. Quantize all the widths grabbed to these 5 widths if they differ from these widths
    by a small number.
10. For each width in these 5 widths do the following steps (11-13)
11. Grab all the elements with the width same as the current width
12. Find the parent element of all of these same width elements and grab the most
    common one among them which is probably the required parent element of all the
    required posts.
13. Check if the big element found using 12 is the required one by comparing the
    sum of heights of all the same width elements and the height of the big element.
    If the big element is the required element continue. If not go to the next width.
14. For all the posts try and find if most of them have id attributes. If so then
    just return the regex for the id. If id doesnot exist, check if they have a
    class attribute and return it. If no class is present try and find other attributes
    that are common among children. If no atrribute can be found return the indices
    of children that are valid.

**Usage**
Pass the soup and driver object to find_posts function in getPosts.py and it should
return the soup of the big element and posts.
eg. main_selector_soup, row_selector_soup = find_posts(soup, driver, home_path)
If this doesn't work, we can probably grab these manually and continue with other
parts of autoparser.

##Finding the required fields from the grabbed posts.

#User name

**Algorithm/Overview of method**
