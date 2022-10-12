from flask import render_template
from app import webapp


@webapp.route('/')
def main():
    return render_template("main.html")
