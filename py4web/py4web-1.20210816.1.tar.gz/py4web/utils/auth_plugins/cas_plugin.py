class CAS(SSO):

    name = "cas"
    maps = {}

    ### methods that must be overwritten

    def __init__(self, cas_provider=None, cas_domains=None):
        self.parameters = dict(
            cas_provider = cas_providers,
            cas_domains = cas_domains
        )
        self.cas_actions = dict(

        )
        
    def get_login_url(self):
        """returns the url for login"""
        return ""

    def handle_request(self, auth, path, get_vars, post_vars):
        if path == "login":
            redirect(self.get_login_url())
        elif path == "callback":
            self._handle_callback(auth, get_vars)
        else:
            abort(404)

    def callback(self, get_vars):
        return {}




elif args[0] == 'cas' and not self.settings.cas_provider:
            if args(1) == self.settings.cas_actions['login']:
                return self.cas_login(version=2)
            elif args(1) == self.settings.cas_actions['validate']:
                return self.cas_validate(version=1)
            elif args(1) == self.settings.cas_actions['servicevalidate']:
                return self.cas_validate(version=2, proxy=False)
            elif args(1) == self.settings.cas_actions['proxyvalidate']:
                return self.cas_validate(version=2, proxy=True)
            elif (args(1) == 'p3'
                  and args(2) == self.settings.cas_actions['servicevalidate']):
                return self.cas_validate(version=3, proxy=False)
            elif (args(1) == 'p3'
                  and args(2) == self.settings.cas_actions['proxyvalidate']):
                return self.cas_validate(version=3, proxy=True)
            elif args(1) == self.settings.cas_actions['logout']:
                return self.logout(next=request.vars.service or DEFAULT)

            
                
                db.define_table(
                    settings.table_cas_name,
                    Field('user_id', reference_table_user, default=None,
                          label=self.messages.label_user_id),
                    Field('created_on', 'datetime', default=now),
                    Field('service', requires=IS_URL()),
                    Field('ticket'),
                    Field('renew', 'boolean', default=False),
                    *settings.extra_fields.get(settings.table_cas_name, []),
                    **dict(
                        migrate=self._get_migrate(
                            settings.table_cas_name, migrate),
                        fake_migrate=fake_migrate))

        if settings.cas_provider:  # THIS IS NOT LAZY
            settings.actions_disabled = \
                ['profile', 'register', 'change_password',
                 'request_reset_password', 'retrieve_username']
            from gluon.contrib.login_methods.cas_auth import CasAuth
            maps = settings.cas_maps
            if not maps:
                table_user = self.table_user()
                maps = dict((name, lambda v, n=name: v.get(n, None)) for name in
                            table_user.fields if name != 'id'
                            and table_user[name].readable)
                maps['registration_id'] = \
                    lambda v, p=settings.cas_provider: '%s/%s' % (p, v['user'])
            actions = [settings.cas_actions['login'],
                       settings.cas_actions['servicevalidate'],
                       settings.cas_actions['logout']]
            settings.login_form = CasAuth(
                casversion=2,
                urlbase=settings.cas_provider,
                actions=actions,
                maps=maps)
        return self

    def cas_login(self,
                  next=DEFAULT,
                  onvalidation=DEFAULT,
                  onaccept=DEFAULT,
                  log=DEFAULT,
                  version=2,
                  ):
        request = current.request
        response = current.response
        session = current.session
        db, table = self.db, self.table_cas()
        session._cas_service = request.vars.service or session._cas_service
        if request.env.http_host not in self.settings.cas_domains or \
                not session._cas_service:
            raise HTTP(403, 'not authorized')

        def allow_access(interactivelogin=False):
            row = table(service=session._cas_service, user_id=self.user.id)
            if row:
                ticket = row.ticket
            else:
                ticket = 'ST-' + web2py_uuid()
                table.insert(service=session._cas_service,
                             user_id=self.user.id,
                             ticket=ticket,
                             created_on=request.now,
                             renew=interactivelogin)
            service = session._cas_service
            query_sep = '&' if '?' in service else '?'
            del session._cas_service
            if 'warn' in request.vars and not interactivelogin:
                response.headers[
                    'refresh'] = "5;URL=%s" % service + query_sep + "ticket=" + ticket
                return A("Continue to %s" % service,
                         _href=service + query_sep + "ticket=" + ticket)
            else:
                redirect(service + query_sep + "ticket=" + ticket)
        if self.is_logged_in() and 'renew' not in request.vars:
            return allow_access()
        elif not self.is_logged_in() and 'gateway' in request.vars:
            redirect(session._cas_service)

        def cas_onaccept(form, onaccept=onaccept):
            if onaccept is not DEFAULT:
                onaccept(form)
            return allow_access(interactivelogin=True)
        return self.login(next, onvalidation, cas_onaccept, log)

    def cas_validate(self, version=2, proxy=False):
        request = current.request
        db, table = self.db, self.table_cas()
        current.response.headers['Content-Type'] = 'text'
        ticket = request.vars.ticket
        renew = 'renew' in request.vars
        row = table(ticket=ticket)
        success = False
        if row:
            userfield = self.settings.login_userfield or 'username' \
                if 'username' in table.fields else 'email'
            # If ticket is a service Ticket and RENEW flag respected
            if ticket[0:3] == 'ST-' and \
                    not ((row.renew and renew) ^ renew):
                user = self.table_user()(row.user_id)
                row.delete_record()
                success = True

        def build_response(body):
            xml_body = to_native(TAG['cas:serviceResponse'](
                    body, **{'_xmlns:cas': 'http://www.yale.edu/tp/cas'}).xml())
            return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_body
        if success:
            if version == 1:
                message = 'yes\n%s' % user[userfield]
            elif version == 3:
                username = user.get('username', user[userfield])
                message = build_response(
                    TAG['cas:authenticationSuccess'](
                        TAG['cas:user'](username),
                        TAG['cas:attributes'](
                            *[TAG['cas:' + field.name](user[field.name])
                              for field in self.table_user()
                              if field.readable])))
            else:  # assume version 2
                username = user.get('username', user[userfield])
                message = build_response(
                    TAG['cas:authenticationSuccess'](
                        TAG['cas:user'](username),
                        *[TAG['cas:' + field.name](user[field.name])
                          for field in self.table_user()
                          if field.readable]))
        else:
            if version == 1:
                message = 'no\n'
            elif row:
                message = build_response(TAG['cas:authenticationFailure']())
            else:
                message = build_response(
                    TAG['cas:authenticationFailure'](
                        'Ticket %s not recognized' % ticket,
                        _code='INVALID TICKET'))
        raise HTTP(200, message)
