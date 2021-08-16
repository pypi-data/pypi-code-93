from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
import json


class NewSAMLPlugin:

    name = "NewSAML"
    label = "NewSAML"

    def __init__(self, cert=cert, IDP_entityId=IDPentityId, https=https, port=port, appname=appname, ssourl=ssourl, logouturl=logouturl):
        self.cert = cert
        self.appname = appname
        self.IDP_entityId=IDP_entityId
        self.https=https
        self.port=port
        self.ssourl=ssourl
        self.logouturl=logouturl

    def init_saml_auth(req):
        SAML_SETTINGS = r'''{
        "strict": true,
        "debug": true,
        "sp": {
            "entityId": "http://localhost:8000",
            "assertionConsumerService": {
                "url": "https://localhost:8000/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            }},
            "idp": {
                "entityId": "http://www.okta.com/XXXXX",
                "singleSignOnService": {
                    "url": "https://dev-XXXXXXX.okta.com/app/dev-XXXXX_py4webtest_1/XXXXX/sso/saml",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                },
                "singleLogoutService": {
                    "url": "https://dev-XXXX-admin.okta.com/login/admin/signout",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                },
                "x509cert": "XXXX"   }
        }'''
        # auth = OneLogin_Saml2_Auth(req, custom_base_path=SAML_PATH)
        auth = OneLogin_Saml2_Auth(req, json.loads(SAML_SETTINGS))
        return auth

    def prepare_bottle_request(req):
        url_data = urlparse(req.url)
        return {
            'https': 'on' if https==True else 'off',
            'http_host': req.get_header('host'),
            'server_port': port,
            'script_name': req.fullpath,
            'get_data': req.query,
            'post_data': req.forms,
            # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
            # 'lowercase_urlencoding': True,
            'query_string': req.query_string
        }

    def idp_redirect:
        req = prepare_bottle_request(request)
        auth = init_saml_auth(req)
        redirect (auth.login())
    
    def acs():
        req = prepare_bottle_request(request)
        auth = init_saml_auth(req)
        auth.process_response()
        errors = auth.get_errors()
        if not errors:
            if auth.is_authenticated():
                session['samlUserdata'] = auth.get_attributes()
                #print (session['samlUserdata']['email'])
                emaillist = session['samlUserdata']['email']
                email=', '.join(emaillist)
                #print (email) 
                user=db(db.auth_user.email==email).select(db.auth_user.id).first()
                #print (user.id)
                session["user"] = {"id": user.id}
                session["recent_activity"] = calendar.timegm(time.gmtime())
                session["uuid"] = str(uuid.uuid1())
            # if 'RelayState' in req['post_data']:
            #   redirect(req['post_data']['RelayState'])
            else: print('Not authenticated')
        else: print("Error when processing SAML Response: {}".format(', '.join(errors)))

                                                                                                                                                                                                              79,13        Ende

