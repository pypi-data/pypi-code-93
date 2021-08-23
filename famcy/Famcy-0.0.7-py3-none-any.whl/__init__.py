# -*- coding: UTF-8 -*-
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session, abort
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_sijax

import importlib
from Famcy._util_.file_utils import *
from Famcy._util_._fblock import FBlock
from Famcy._util_._submit_type import SubmitType
from gadgethiServerUtils.file_basics import *

PACKAGE_NAME = "Famcy"
USER_DEFAULT_FOLDER = "_CONSOLE_FOLDER_/"
FamcyBlock = FBlock

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
migrate = Migrate()

sijax = flask_sijax

def create_app():

    app = Flask(__name__)

    app.config['SECRET_KEY'] = '00famcy00!2'
    app.config['user_default_folder'] = USER_DEFAULT_FOLDER
    app.config['package_name'] = PACKAGE_NAME
    app.config.update(read_config_yaml(app.config.get('user_default_folder','')+"famcy.yaml"))
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('db_url','')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
    app.config["SIJAX_JSON_URI"] = '/static/js/sijax/json2.js'

    db.init_app(app)
    migrate.init_app(app, db)
    sijax.Sijax().init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'iam.login'
    login_manager.init_app(app)

    from Famcy._util_.iam_utils import FamcyUser

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return FamcyUser.query.get(int(user_id))

    # blueprint for non-auth routes of app
    from Famcy._services_._main_service import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for auth parts of app
    from Famcy._services_.iam_service import iam as iam_blueprint
    app.register_blueprint(iam_blueprint)

    return app

# ------ above is the flask part -----------

# ------ Famcy system utility functions -------
def generate_content_obj(page_header, page_content, submission_list=None):
    """
    This is the helper function to generate the content
    object for the page. Like compiling the content
    """
    if submission_list == None:
        submission_list = []
        for _ in range(len(page_content)):
            if isinstance(page_content[_], list):
                temp = [lambda i,**c: None for __ in range(len(page_content[_]))]
                submission_list.append(temp)
            else:
                submission_list.append(None)

    ret_list = []
    for i in range(len(page_content)):

        if isinstance(page_header["type"][i], list):
            temp = []
            if submission_list == None:
                submission_list[i] = [lambda i,**c: None for _ in range(len(page_content[i]))]
            for j in range(len(page_header["type"][i])):
                temp.append(globals()[page_header["type"][i][j]](_submission_handler=submission_list[i][j], 
                    **page_content[i][j]))
            ret_list.append(temp)

        else:
            ret_list.append(globals()[page_header["type"][i]](_submission_handler=submission_list[i], 
                **page_content[i]))

    return ret_list

def put_submissions_to_list(sub_dict, submission_id):
    """
    This is the helper function to put the
    submission content to a list of arguments
    - Input:
        * sub_dict: submission dictionary
        * submission_id: id for the submission
    """
    ordered_submission_list = []
    btn_info = []
    for key in sorted(list(sub_dict.keys())):
        # Guard the button case. 
        if submission_id not in key:
            continue
        elif "mb" in key:
            btn_info = sub_dict[key]
            continue
        ordered_submission_list.append(sub_dict[key])

    ordered_submission_list.append(btn_info)

    return ordered_submission_list

# Import Fblocks from default and custom folders. 
# ------------------------------
famcy_blocks = {
    "_fblocks_": [],
    USER_DEFAULT_FOLDER + "_custom_fblocks_": []
}

block_list = []
for fblock_group in famcy_blocks.keys():
    famcy_blocks[fblock_group] = listdir_exclude(fblock_group, exclude_list=[".", "_"])
    block_list.extend(famcy_blocks[fblock_group])

# Check no repeat names
assert len(block_list) == len(list(set(block_list)))

for fblock_group in famcy_blocks.keys():
    for block in famcy_blocks[fblock_group]:
        fblock_group = fblock_group.replace('/', '.')
        globals()[block] = getattr(importlib.import_module(PACKAGE_NAME+"."+fblock_group+"."+block+"."+block), block)

SijaxSubmit = SubmitType
