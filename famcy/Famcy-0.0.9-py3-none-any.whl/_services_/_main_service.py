import os
import json
import urllib
from Famcy import sijax
from .._util_.dashboard_utils import *
from .._util_._sijax import *
from flask import g, render_template, redirect, url_for, session, flash, request, Blueprint, current_app, render_template_string
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

# Main Routing function
# -------------------------
@main.route('/')
def home():
    return redirect(url_for("main.generate_dashboard"))

@sijax.route(main, "/dashboard", methods=['GET', 'POST'])
def generate_dashboard():
    # handle dashboard submit
    if g.sijax.is_sijax_request:
        g.sijax.register_object(SijaxHandler)
        return g.sijax.process_request()

    # handle switch tab from dashboard to others
    if request.method == 'POST':
        tab_name = request.form["side_bar_btn"]
        safe_tab_name = urllib.parse.quote_plus(tab_name)
        return redirect(url_for("main.generate_tab_page", tab=safe_tab_name))

    html_header = dashboardHTMLHeader(current_app.config.get("console_title", ""), current_app.config.get("console_description", ""))
    side_bar = dashboardSideBar(current_app.config.get("side_bar_title", ""), current_app.config.get("side_bar_hierachy", {}))
    nav_bar = dashboardNavBar("登入", os.path.join(current_app.config.get("main_url", ""), "static", "image/login.png"))
    
    content, extra_script = user_defined_contents(current_app.config.get("main_page", {}))
    end_js = dashboardJavaScript()
    color_theme = setColorTheme(main_color="#edaf00")
    load_spinner=generateLoader("Ellipsis")
    
    return render_template("index.html", load_spinner=load_spinner, color_theme=color_theme, html_header=html_header, side_bar=side_bar, nav_bar=nav_bar, content=content, extra_script=extra_script, end_js=end_js)
    
@sijax.route(main, "/dashboard/<tab>", methods=['GET', 'POST'])
@login_required
def generate_tab_page(tab):
    # Home page redirect
    if request.method == 'POST':
        if g.sijax.is_sijax_request:
            g.sijax.register_object(SijaxHandler)
            return g.sijax.process_request()

    if tab == '-':
        return redirect(url_for("main.generate_dashboard"))

    tab_name = urllib.parse.unquote(tab)

    html_header = dashboardHTMLHeader(current_app.config.get("console_title", ""), current_app.config.get("console_description", ""))
    side_bar = dashboardSideBar(current_app.config.get("side_bar_title", ""), current_app.config.get("side_bar_hierachy", {}), title_style="bx-game", side_bar_style={"管理": "bxl-python"})
    nav_bar = dashboardNavBar(current_user.name, current_user.profile_pic_url)
    
    content, extra_script = user_defined_contents(tab)
    end_js = dashboardJavaScript()
    color_theme = setColorTheme(main_color="#edaf00")
    load_spinner=generateLoader("Ellipsis")

    return render_template("index.html", load_spinner=load_spinner, color_theme=color_theme, html_header=html_header, side_bar=side_bar, nav_bar=nav_bar, content=content, extra_script=extra_script, end_js=end_js)
    
