'''
This file contains the renderings of the user-friendly pages for the
HTTP error codes.
'''

from flask import render_template


def page_not_found(e):
    return render_template('404.html', message=e.description), 404


def bad_request(e):
    return render_template('400.html', message=e.description), 400


def unauthorized(e):
    return render_template('401.html', message=e.description), 401


def forbidden(e):
    return render_template('403.html', message=e.description), 403


def gone(e):
    return render_template('410.html', message=e.description), 410
