from bs4 import BeautifulSoup
import requests


def get_result_pages_url(url):
    """
    function to generate links to all subsequent search results pages

    Input arguments: 'URL'   -- str  -- starting page URL, a page from search results

    Returns: 'List_of_all_URLs' -- list -- list of all subsequent URLs
             'total_results'    -- int  -- total number of jobs postings found


    returns a list of URLs of all search results pages
    """

    # get the HTML of the first search results page

    r = requests.get(url)
    content = r.text

    # make a soup out of the first page of search results
    soup = BeautifulSoup(content, 'lxml')
    # extract the number of search results
    num_results_str = soup.find('div', {'id': 'searchCount'}).text

    # parse the string and extract the total number (4th element), replace comma with an empty space, convert to int
    total_results = int(num_results_str.split()[3].replace(',', ''))

    # add the common part between all search pages
    next_pages_links = "https://www.indeed.ca" + soup.find('div', {'class': 'pagination'}).find('a').get('href')[:-2]

    # create empty list to store URLs of all search results pages
    List_of_all_URLs = []

    # add the first page to the 'List_of_all_URLs'
    List_of_all_URLs.append(next_pages_links)

    # add different starting positions for subsequent search results pages to 'List_of_all_URLs'
    for start_position in range(20, total_results, 20):
        List_of_all_URLs.append(next_pages_links + str(start_position))

    return List_of_all_URLs[:2]
