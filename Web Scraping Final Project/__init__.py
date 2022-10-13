from flask import Flask

webapp = Flask(__name__)
webapp.config['SECRET_KEY'] = 'you-will-never-guess'

from app import main
# from app import get_result_pages_url
# from app import scrape_job_info
# from app import scrape_job_links
