from flask import Blueprint, render_template, redirect, url_for, request, current_app, g
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required

from Famcy import put_submissions_to_list, sijax
from Famcy._util_.iam_utils import *
from .._util_._sijax import SijaxHandler

import os

iam = Blueprint('iam', __name__)

@sijax.route(iam, "/login", methods=['GET', 'POST'])
def login():
    if g.sijax.is_sijax_request:
        g.sijax.register_object(SijaxHandler)
        return g.sijax.process_request()

    html_header, content, extra_script, end_js, _, color_theme, load_spinner = login_page_contents()
    return render_template("login.html", load_spinner=load_spinner, extra_script=extra_script, color_theme=color_theme, html_header=html_header, content=content, end_js=end_js)

@sijax.route(iam, "/signup", methods=['GET', 'POST'])
def signup():
    if g.sijax.is_sijax_request:
        g.sijax.register_object(SijaxHandler)
        return g.sijax.process_request()

    html_header, content, extra_script, end_js, _, color_theme, load_spinner = signin_page_contents()
    return render_template("login.html", load_spinner=load_spinner, extra_script=extra_script, color_theme=color_theme, html_header=html_header, content=content, end_js=end_js)

@sijax.route(iam, "/profile", methods=['GET', 'POST'])
@login_required
def profile_page():
    if g.sijax.is_sijax_request:
        g.sijax.register_object(SijaxHandler)
        return g.sijax.process_request()

    html_header, side_bar, nav_bar, content, extra_script, end_js, _, color_theme, load_spinner = profile_page_contents()
    return render_template("index.html", load_spinner=load_spinner, extra_script=extra_script, color_theme=color_theme, html_header=html_header, side_bar=side_bar, nav_bar=nav_bar, content=content, end_js=end_js)


@iam.route('/dashboard/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))