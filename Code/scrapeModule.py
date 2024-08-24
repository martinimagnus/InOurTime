from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd



# ++++++++++++ GET LINKS 

# Helper-functions to get Links
def getTitle(url):


    '''GET THE EPISODE TITLES ON A SITE
    :params 
        url: website'''

    # Initiate Driver Object and Navigate to website
    driver = webdriver.Chrome()
    driver.get(url)

    #Get WebElement
    '''Eplanation of this XPath: 
    - //div[@class="grid 2/3@bpw2 2/3@bpe"] ---> select everything that is under a div-tag with this attribute
    - //li ---> select everything htat is under every list tag
    - //div[@class="programme__body"] ---> select every div that has this tag
    - //span[@class="programme__title "] ---> select all the span tags with this attribute'''
    title_element = driver.find_elements(By.XPATH, '//div[@class="grid 2/3@bpw2 2/3@bpe"]//li//div[@class="programme__body"]//span[@class="programme__title "]')

    # Get text and store in list
    title_lst = [element.text for element in title_element]

    driver.close()
    return title_lst

def getHrefs(driver):
    '''
    on a given site, get all episode links
    '''

    # get elements
    anchor_elements = driver.find_elements(By.XPATH, '//div[@class="grid 2/3@bpw2 2/3@bpe"]//li//div[@class="programme__body"]//a[@class="br-blocklink__link block-link__target"]')

    # get hrefs out of elements
    href_lst = [element.get_attribute("href") for element in anchor_elements]

    return href_lst

def pagination(driver):
    try:
        next_button = driver.find_element(By.XPATH, "//li[@class='pagination__next']/a[@rel='next']")  # check if page has path
        if next_button.is_enabled():
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # scroll down because of cookie field
            next_button.click()
            return True  # Pagination was successful, continue
    except NoSuchElementException:
        return False  # No more pages to navigate, exit the loop

    return False  # Default to exiting the loop if no conditions met

# Combine Helper-functions 
def ensembleHrefs(url):

    '''Returns a list of all ULRs of the Episodes. 
    Goes to given url, gets all episode urls and paginates
    '''
    
    # initialize Driver and go to URL
    driver = webdriver.Chrome()
    driver.get(url)

    # Create List to store URLs in 
    href_motherlist = []

    # While current url has "next" button, get all URLs from current URL, then paginate
    while True: 

        href_lst = getHrefs(driver)     # apply getHref function to the current page
        href_motherlist.append(href_lst)  # Append a copy of the href-list to the mother list

        # now pagination function is executed. "if not"-expression checks outcome of pagination function after execution
        # if result of pagination=True -> continue while loop. 
        if not pagination(driver):  # If pagination returns False, exit the While-loop
            break

    driver.close()


    # flatten the list
    href_motherlist_flat = [item for sublist in href_motherlist for item in sublist]

    return href_motherlist_flat




# ++++++++++++ GET TITLE AND EPISODE DESCRIPTION
def ensembleTitleContent(list_of_links):    
    ''' Returns a Dataframe with columns 'title' and 'content' of each episode
    '''

    # Initialize Driver
    driver = webdriver.Chrome()

    # Create holder lists where each content and title is stored
    paragraphs_mother_lst = []
    title_mother_lst = []
    date_mother_lst = []

    # Loop through each link which directs to one episode
    for link in list_of_links:

        # Navigate to episode website
        driver.get(link)

        #--- TITLE
        # locate title element
        title_element = driver.find_elements(By.XPATH, '//h1[@class="no-margin"]')
        # Extract title-text and append to list
        title_mother_lst.append(title_element[0].text)
        

        #--- DATE
        # locate date element
        date_element = driver.find_element(By.XPATH, '//span[@class="broadcast-event__date text-base timezone--date"]')
        # Extract date-text and append to list
        date_mother_lst.append(date_element.text)

        #--- CONTENT
        # locate content element
        content_element = driver.find_elements(By.XPATH, '//div[@class="synopsis-toggle__long"]//p')

        # Loop through each <p> element and extract the content-text
        paragraph_text = []
        for paragraph in content_element:
            text = paragraph.get_attribute("textContent")
            paragraph_text.append(text)
        # append list of paragraph contents to mother content list
        paragraphs_mother_lst.append(paragraph_text)


    driver.close()

    # Create a dataframe with title and content
    df_ = pd.DataFrame({'title': title_mother_lst,
                        'date': date_mother_lst,
                        'content': paragraphs_mother_lst})


    return df_
