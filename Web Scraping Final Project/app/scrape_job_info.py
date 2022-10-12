import boto3
from app.forms import JobSearch
import requests
from bs4 import BeautifulSoup
from flask import render_template, redirect, url_for, request
import re
from app import scrape_job_links, get_result_pages_url
from app import webapp
from zappa.asynchronous import task


@webapp.route('/search', methods=['GET', 'POST'])
def search():
    form = JobSearch()

    if form.validate_on_submit():
        url_parsed = 'https://ca.indeed.com/jobs?q=' + form.job_title.data + '&l=' + form.location.data
        return redirect(url_for('scrape_job_info', url=url_parsed))
    return render_template('search.html', form=form)


comprehend_client = boto3.client('comprehend', region_name="us-east-1")


def detect_entities(text):
    comprehend = boto3.client('comprehend', region_name="us-east-1")
    response = comprehend.detect_entities(Text=text, LanguageCode="en")
    return response


def comprehend_text(text):
    result = detect_entities(text)
    comprehend_description = []
    for data in result['Entities']:
        if data['Type'] == 'TITLE':
            comprehend_description.append(data['Text'])

    return comprehend_description


# https://ca.indeed.com/jobs?q=web+developer&l=Toronto%2C+ON
@webapp.route('/jobs', methods=['GET', 'POST'])
def scrape_job_info():
    """
    function to scrape individual job pages from indeed.ca
    used by the function 'scrape_job_links_and_info'

    scrapes individual job postings and saves results
    to a list 'scraping_results_dict'

    Input arguments: job_search_results -- list -- list of <div> tags with job postings
                                                   from a search results page
    """
    url = request.args.get('url')
    results = get_result_pages_url.get_result_pages_url(url)
    job_url_list = scrape_job_links.scrape_job_links(results)  # list of the urls of each job posting
    scrape_jobs_entities_per_page(job_url_list)

    return render_template('jobs.html')


@task(capture_response=True)
def scrape_jobs_entities_per_page(job_url_list):

    job_entities_list = []
    for job_url in job_url_list:
        # get the HTML code from the job posting page and save it as text to 'job_desc'
        job_html = requests.get(job_url)
        job_desc = job_html.text
        job_desc = BeautifulSoup(job_desc, 'lxml').find(lambda tag: tag.name == 'div' and tag.get('class') == ['jobsearch-jobDescriptionText']).get_text().rstrip()

        # Remove punctuation
        job_content = re.sub(pattern=r'[\!"#$%&\*+,-./:;<=>?@^_`()|~=]', repl=' ', string=job_desc)
        job_content = job_content.replace('\n', ' ')

        job_entities = comprehend_text(job_content[:4000])
        job_entities_list.append(job_entities)

    return {'Entities': job_entities_list}
