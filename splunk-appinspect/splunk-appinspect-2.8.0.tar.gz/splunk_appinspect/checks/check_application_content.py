# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Application content structure standards

Ensure that the application content adheres to Splunk standards.
"""

# Python Standard Libraries
import imghdr
import logging
import os

# Third-Party Libraries
from PIL import Image

# Custom Libraries
import splunk_appinspect


report_display_order = 2
logger = logging.getLogger(__name__)


def _image_attributes(path):
    """ Helper function to return image metadata"""
    try:
        img_obj = Image.open(path)
        img_obj.verify()
        return img_obj.size[0], img_obj.size[1]
    except Exception:
        logger.info("Unable to verify the image, image_path: %s", path)
        return None


def _verify_image_dimensions(relative_path, app, reporter, max_width, max_height):
    """ Helper function calling reporter to update the check result"""
    file_path = os.path.join(*relative_path)
    full_path = app.get_filename(*relative_path)
    image_attr = _image_attributes(full_path)
    if image_attr is None:
        reporter_output = (
            "unable to verify the image, the image file is broken. File: {}"
        ).format(file_path)
        reporter.fail(reporter_output, file_path)
    else:
        width, height = image_attr
        if width > max_width or height > max_height:
            reporter_output = (
                "{} should be {}x{} or less, but was detected as {}x{}. File: {}"
            ).format(relative_path, max_width, max_height, width, height, file_path)
            reporter.fail(reporter_output, file_path)


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_icon_is_png(app, reporter):
    """Check that static/appIcon is a png file"""
    relative_file_path = ["static", "appIcon.png"]
    if app.file_exists(*relative_file_path):
        file_path = os.path.join(*relative_file_path)
        if imghdr.what(app.get_filename(*relative_file_path)) != "png":
            reporter_output = ("static/appIcon must be a png file. File: {}").format(
                file_path
            )
            reporter.fail(reporter_output, file_path)
    else:
        reporter.fail("static/appIcon.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_icon_dimensions(app, reporter):
    """Check that static/appIcon is 36x36px or less"""
    relative_file_path = ["static", "appIcon.png"]
    if app.file_exists(*relative_file_path):
        _verify_image_dimensions(relative_file_path, app, reporter, 36, 36)
    else:
        reporter.fail("static/appIcon.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_icon_2x_is_png(app, reporter):
    """Check that static/appIcon_2x is a png file"""
    relative_file_path = ["static", "appIcon_2x.png"]
    if app.file_exists(*relative_file_path):
        file_path = os.path.join(*relative_file_path)
        if imghdr.what(app.get_filename(*relative_file_path)) != "png":
            reporter_output = ("static/appIcon_2x must be a png file. File: {}").format(
                file_path
            )
            reporter.fail(reporter_output, file_path)
    else:
        reporter.fail("static/appIcon_2x.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_icon_2x_dimensions(app, reporter):
    """Check that static/appIcon_2x is 72x72px or less"""
    relative_file_path = ["static", "appIcon_2x.png"]
    if app.file_exists(*relative_file_path):
        _verify_image_dimensions(relative_file_path, app, reporter, 72, 72)
    else:
        reporter.fail("static/appIcon_2x.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_icon_alt_is_png(app, reporter):
    """Check that static/appIconAlt is a png file"""
    relative_file_path = ["static", "appIconAlt.png"]
    if app.file_exists(*relative_file_path):
        file_path = os.path.join(*relative_file_path)
        if imghdr.what(app.get_filename(*relative_file_path)) != "png":
            reporter_output = ("static/appIconAlt must be a png file. File: {}").format(
                file_path
            )
            reporter.fail(reporter_output, file_path)
    else:
        reporter.not_applicable("static/appIconAlt.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_icon_alt_dimensions(app, reporter):
    """Check that static/appIconAlt.png is 36x36px or less"""
    relative_file_path = ["static", "appIconAlt.png"]
    if app.file_exists(*relative_file_path):
        _verify_image_dimensions(relative_file_path, app, reporter, 36, 36)
    else:
        reporter.not_applicable("static/appIconAlt.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_icon_alt_2x_is_png(app, reporter):
    """Check that static/appIconAlt_2x is a png file"""
    relative_file_path = ["static", "appIconAlt_2x.png"]
    if app.file_exists(*relative_file_path):
        file_path = os.path.join(*relative_file_path)
        if imghdr.what(app.get_filename(*relative_file_path)) != "png":
            reporter_output = (
                "static/appIconAlt_2x must be a png file. File: {}"
            ).format(file_path)
            reporter.fail(reporter_output, file_path)
    else:
        reporter.not_applicable("static/appIconAlt_2x.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_icon_alt_2x_dimensions(app, reporter):
    """Check that static/appIconAlt_2x.png is 72x72px or less"""
    relative_file_path = ["static", "appIconAlt_2x.png"]
    if app.file_exists(*relative_file_path):
        _verify_image_dimensions(relative_file_path, app, reporter, 72, 72)
    else:
        reporter.not_applicable("static/appIconAlt_2x.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_logo_is_png(app, reporter):
    """Check that static/appLogo is a png file"""
    relative_file_path = ["static", "appLogo.png"]
    if app.file_exists(*relative_file_path):
        file_path = os.path.join(*relative_file_path)
        if imghdr.what(app.get_filename(*relative_file_path)) != "png":
            reporter_output = ("static/appLogo must be a png file. File: {}").format(
                file_path
            )
            reporter.fail(reporter_output, file_path)
    else:
        reporter.not_applicable("static/appLogo.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_logo_dimensions(app, reporter):
    """Check that static/appLogo.png is 160x40px or less"""
    relative_file_path = ["static", "appLogo.png"]
    if app.file_exists(*relative_file_path):
        _verify_image_dimensions(relative_file_path, app, reporter, 160, 40)
    else:
        reporter.not_applicable("static/appLogo.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_logo_2x_is_png(app, reporter):
    """Check that static/appLogo_2x is a png file"""
    relative_file_path = ["static", "appLogo_2x.png"]
    if app.file_exists(*relative_file_path):
        file_path = os.path.join(*relative_file_path)
        if imghdr.what(app.get_filename(*relative_file_path)) != "png":
            reporter_output = ("static/appLogo_2x must be a png file. File: {}").format(
                file_path
            )
            reporter.fail(reporter_output, file_path)
    else:
        reporter.not_applicable("static/appLogo_2x.png does not exist.")


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.2.1")
def check_app_logo_2x_dimensions(app, reporter):
    """Check that static/appLogo_2x.png is 320x80px or less"""
    relative_file_path = ["static", "appLogo_2x.png"]
    if app.file_exists(*relative_file_path):
        _verify_image_dimensions(relative_file_path, app, reporter, 320, 80)
    else:
        reporter.not_applicable("static/appLogo_2x.png does not exist.")
