# -*- coding=utf-8 -*-

from flask import send_file, send_from_directory, make_response
import os
import urllib
from urllib.parse import quote


class FlaskHelper(object):

    @staticmethod
    def make_download_response(**params):
        directory = params.get('directory')
        file_name = params.get('file_name')
        response = make_response(send_from_directory(directory, file_name, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(file_name.encode().decode('latin-1'))
            
        return response
