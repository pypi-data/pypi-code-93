def login_template(username, password):
    template = {
        'userName': username,
        'password': password,
        'captcha': '',
        'portalType': 'CBCS'
    }
    return template


def register_course_template(student_id, subj_id, esetId, faculty_name):
    template = {
        'instId': '1',
        'stuId': student_id,
        'subjId': subj_id,
        'sxnId': '0',
        'esetId': esetId,
        'facultyName': faculty_name
    }

    return template


def drop_course_template(subj_cd, eset_id):
    template = {
        'instId': '1',
        'subjId': subj_cd,
        'sxnId': '0',
        'esetId': eset_id
    }
    return template


def forgot_password_submit_username(username):
    template = {
        'reqType': 'validateUser',
        'userId': username
    }
    return template


def forgot_pass_submit_phone_email(username, phone_number, email):
    template = {
        'reqType': 'validateAndsendOTP',
        'userId': username,
        'mobileNo': phone_number,
        'email': email
    }
    return template


def forgot_pass_submit_otp(username, otp):
    template = {
        'reqType': 'validateOTP',
        'userId': username,
        'otp': otp
    }
    return template


def submit_new_password(username, new_password):
    template = {
        'reqType': 'changePassword',
        'userId': username,
        'newPassword': new_password
    }
    return template
