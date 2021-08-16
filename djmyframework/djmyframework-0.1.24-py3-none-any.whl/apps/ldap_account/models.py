# -*- coding: utf-8 -*-

import shutil
import typing

from ldaptor._encoder import to_bytes

from framework.apps import get_app_path
from framework.models import BaseNameModel, models
from framework.translation import _
from framework.utils import mkdirs
from framework.utils.cache import CacheAttribute
from framework.utils.myenum import Enum
from myadmin.models import Role, User, UserInfo
from .settings import DBPATH

from ldaptor.ldiftree import *
import os

APP_PATH = get_app_path('ldap_account')


def get_db_path():
    tpl_db_path = os.path.join(APP_PATH, 'ldiftree')
    tmp_db_path = DBPATH

    if not os.path.exists(tmp_db_path):
        shutil.rmtree(tmp_db_path, ignore_errors=True)
        shutil.copytree(tpl_db_path, tmp_db_path)
    OU_PEOPLE_DIR = os.path.join(DBPATH, 'dc=com.dir', 'dc=example.dir', 'ou=user.dir')
    OU_ROLE_DIR = os.path.join(DBPATH, 'dc=com.dir', 'dc=example.dir', 'ou=role.dir')
    mkdirs(OU_PEOPLE_DIR)
    mkdirs(OU_ROLE_DIR)

    return tmp_db_path


# mail 字段是 mindoc 需要
cn_tpl = '''dn: cn={cn},ou=user,dc=example,dc=com
objectClass: posixAccount
uid: {uid}
cn: {cn}
sn: {sn}
alias: {alias}
uidNumber: {uidNumber}
status: {status}
email: {email}
mail: {email}
employeeId: {employee_id}
userPassword: {userPassword}


'''

ou_role_tpl = '''dn: cn={cn},ou=role,dc=example,dc=com
cn: {cn}
gidNumber: {gidnumber}
parent: {parent}
alias: {alias}
description: {desc}
objectclass: posixGroup
objectclass: top
{memberuid}


'''

dc_tpl = '''dn: dc=example,dc=com
objectClass: dcObject
dc: example'''


# sourceStrin=1234546
# passlib.hash.ldap_salted_sha1.encrypt('123456')
# '{SSHA}TgL7DCvwD6UkA4mgcOkEUJf2RdSZ0xqj'


class AccessDomain(BaseNameModel):
    """访问域"""

    class Status(Enum):
        Enable = 0, _('开启')
        Disable = 1, _('禁用')

    bindpw = models.CharField(verbose_name=_('访问密钥'), max_length=30, default='', null=False)
    access_address = models.CharField(verbose_name=_('访问地址'), max_length=256, default='', null=False)
    status = models.IntegerField(verbose_name=_('状态'), choices=Status.member_list(), default=Status.Enable)

    role = models.ManyToManyField(Role, verbose_name=_('允许访问的角色'))

    @property
    def is_enable(self):
        return self.status == self.Status.Enable

    @property
    def basedn(self):
        return 'dc=%s,dc=com' % self.name

    @property
    def authdn(self):
        return 'cn=%s,ou=user,%s' % (self.name, self.basedn)

    def save(self, *args, **kwargs):
        self.create_ldap_access_user()
        if self.status == self.Status.Disable:
            self.remove_ldap_db_path()
        ret = super().save(*args, **kwargs)
        #        self.generate_db()
        return ret

    def delete(self, *args, **kwargs):
        self.remove_ldap_db_path()
        super().delete(*args, **kwargs)

    def generate_db(self):
        """
        生成  ldap 数据库
        :return:
        """

        roles = self.role.prefetch_related('parent').prefetch_related('user_set').distinct()
        for user in User.get_normal_user_list().prefetch_related('userinfo_set').filter(role__in=roles).distinct():
            self.create_user(user)
        for role in roles:
            self.create_role(role)

    def get_ldap_access_user(self):
        ldap_access_user = User()
        ldap_access_user.username = self.name
        ldap_access_user.alias = self.alias
        ldap_access_user.set_password(self.bindpw)
        _user_info = UserInfo()
        _user_info.email = '%s@%s.com' % (self.name, self.name)
        ldap_access_user.user_info = _user_info
        return ldap_access_user

    def remove_ldap_db_path(self):
        domain_db_path = self.get_domain_db_path()
        if os.path.isdir(domain_db_path):
            os.path.remove(domain_db_path)

    def create_ldap_access_user(self):
        return self.create_user(self.get_ldap_access_user())

    def delete_ldap_access_user(self):
        return self.delete_user(self.get_ldap_access_user())

    def get_domain_db_path(self):

        return os.path.join(DBPATH, 'dc=com.dir', 'dc=%s.dir' % self.name)

    def create_db_dir(self, *dir_name):
        db_dir = os.path.join(self.get_domain_db_path(), *dir_name)
        mkdirs(db_dir)
        return db_dir

    @CacheAttribute
    def user_db_path(self):
        return self.create_db_dir('ou=user.dir')

    @CacheAttribute
    def role_db_path(self):
        return self.create_db_dir('ou=role.dir')

    def create_user(self, user: User):
        file_name = 'cn=%s.ldif' % user.username
        user_info = user.user_info
        employee_id = email = ''
        if user_info:
            employee_id = user_info.employee_id
            email = user_info.email
        save_path = os.path.join(self.user_db_path, file_name)
        password_tuple = user.password.split('$', 1)
        secret = '{SSHA}%s' % (password_tuple[1] if len(password_tuple) > 1 else '')
        ldap_cn_str = ''
        with open(save_path, 'w') as f:
            ldap_cn_str = cn_tpl.format(cn=user.username, sn=user.alias[0], uid=user.username, alias=user.alias,
                                        uidNumber=user.id,
                                        userPassword=secret, email=email, employee_id=employee_id, status=user.status)
            # f.write(ldap_cn_str)
        return ldap_cn_str

    def delete_user(self, user):
        file_name = 'cn=%s.ldif' % user.username
        save_path = os.path.join(self.user_db_path, file_name)
        if os.path.exists(save_path):
            os.remove(save_path)

    def create_role(self, role: Role):
        file_name = 'cn=%s.ldif' % role.name
        ldap_cn_str = ''
        if role.type == Role.RoleType.GROUP:
            parent = ''
            # todo 改为域限制
            if role.parent:
                parent = role.parent.name
            ou_role_dir = self.role_db_path
            save_path = os.path.join(ou_role_dir, file_name)
            memberuid_list = '\n'.join(['memberUid: %s' % v.username for v in role.user_set.all()])

            with open(save_path, 'w') as f:
                ldap_cn_str = ou_role_tpl.format(cn=role.name, parent=parent, gidnumber=role.id, alias=role.alias,
                                                 desc=role.remark, memberuid=memberuid_list)
                # f.write(ldap_cn_str)
        return ldap_cn_str

    def delete_role(self, role: Role):
        file_name = 'cn=%s.ldif' % role.name
        save_path = os.path.join(self.role_db_path, file_name)
        if os.path.exists(save_path):
            os.remove(save_path)

    class Meta:
        pass


# @receiver(post_save, sender=User, dispatch_uid="user_save_ldap")
def user_save_ldap(sender, instance: User, update_fields=None, **kwargs):
    user: User = instance

    access_domain_list: typing.List[AccessDomain] = user.get_resource('access_domain')

    for access_domain in access_domain_list:
        if access_domain.is_enable and user.status == User.Status.NORMAL and update_fields is None:
            access_domain.create_user(user)
        else:
            access_domain.delete_user(user)


# @receiver(pre_delete, sender=User, dispatch_uid="user_delete_ldap")
def user_delete_ldap(sender, instance: User, **kwargs):
    for access_domain in instance.get_resource('access_domain'):
        access_domain.delete_user(instance)


###@receiver(post_save, sender=Role, dispatch_uid="role_save_ldap")
def role_save_ldap(sender, instance: Role, **kwargs):
    role = instance
    access_domain_list = role.get_resource('access_domain').values_list('id', flat=True)
    all_access_domain_list: typing.List[AccessDomain] = AccessDomain.objects.all()

    for access_domain in all_access_domain_list:
        if role.type == Role.RoleType.GROUP and access_domain.id in access_domain_list:
            access_domain.create_role(role)
        else:
            access_domain.delete_role(role)


# @receiver(post_delete, sender=Role, dispatch_uid="role_delete_ldap")
def role_delete_ldap(sender, instance: Role, **kwargs):
    role = instance
    access_domain_list: typing.List[AccessDomain] = AccessDomain.objects.all()
    for access_domain in access_domain_list:
        access_domain.delete_role(role)


# @receiver(post_save, sender=UserInfo, dispatch_uid="user_info_save_ldap")
def user_info_save_ldap(sender, instance: UserInfo, **kwargs):
    user = instance.user
    user_save_ldap(sender, user)


# @receiver(pre_delete, sender=UserInfo, dispatch_uid="user_info_delete_ldap")
def user_info_delete_ldap(sender, instance: UserInfo, **kwargs):
    user = instance.user
    user_delete_ldap(sender, user)


# @receiver(m2m_changed, sender=AccessDomain.role.through, dispatch_uid="access_domain_add_role_ldap")
def access_domain_add_role_ldap(sender, action, instance: Role, reverse, model: AccessDomain, pk_set, using, **kwargs):
    if action in ['post_add', 'post_clear', 'post_remove']:
        if reverse and isinstance(instance, Role):
            role_save_ldap(sender, instance)


# @receiver(m2m_changed, sender=User.role.through, dispatch_uid="user_add_role_ldap")
def user_add_role_ldap(sender, action, instance: Role, reverse, model: User, pk_set, using, **kwargs):
    if action in ['post_add', 'post_clear', 'post_remove']:
        if reverse:
            role_save_ldap(sender, instance)
        else:
            user_save_ldap(sender, instance)


def _putEntry(fileName, entry):
    """fileName is without extension."""
    tmp = u'%s.%s.tmp' % (fileName, str(uuid.uuid4()))
    f = open(tmp, 'wb')
    f.write(entry.toWire())
    f.close()
    os.rename(tmp, fileName + u'.ldif')
    return True


@implementer(interfaces.IConnectedLDAPEntry)
class ModelTreeEntry(entry.EditableLDAPEntry,
                     entryhelpers.DiffTreeMixin,
                     entryhelpers.SubtreeFromChildrenMixin,
                     entryhelpers.MatchMixin,
                     entryhelpers.SearchByTreeWalkingMixin,
                     ):
    access_domain = None
    roles = None

    def __init__(self, dn=None, *a, **kw):
        if dn is None:
            dn = u''
        entry.BaseLDAPEntry.__init__(self, dn, *a, **kw)

    def _load(self):
        dc_name = self.get_dc_name()
        data = b''
        it = self.dn.split()
        if len(it) <= 1:
            return
        first_attr_type = self.get_first_attr_type()
        second_attr_type = self.get_ldap_attr_type(it[1])

        self.access_domain: AccessDomain = AccessDomain.objects.filter(
            name=dc_name).first()
        if self.access_domain and second_attr_type.attributeType == 'ou':
            if second_attr_type.value == 'user':
                if first_attr_type.value == dc_name:
                    data = self.access_domain.create_ldap_access_user().encode()
                else:
                    username = first_attr_type.value
                    user = User.get_normal_user_list().filter(role__in=self.access_domain.role.all()).filter(
                        username=username).first()
                    if user:
                        data = self.access_domain.create_user(user).encode()
            elif second_attr_type.attributeType == 'role':
                role_name = username = first_attr_type.value
                role = self.access_domain.role.select_related('parent').prefetch_related(
                    'user_set__userinfo_set').filter(name=role_name).first()
                if role:
                    data = self.access_domain.create_role(role)
        self.genrate_for_receive_data(data)

    def genrate_for_receive_data(self, data):
        parser = StoreParsedLDIF()
        parser.dataReceived(to_bytes(data))
        parser.connectionLost(failure.Failure(error.ConnectionDone()))
        assert parser.done
        entries = parser.seen
        if len(entries) > 0:
            for k, v in entries[0].items():
                self._attributes[k] = attributeset.LDAPAttributeSet(k, v)

    def __search(self,
                 filterText=None,
                 filterObject=None,
                 attributes=(),
                 scope=None,
                 derefAliases=None,
                 sizeLimit=0,
                 timeLimit=0,
                 typesOnly=0,
                 callback=None):
        # todo 转换 django query 限制查询
        results = []
        first_attr_type = self.get_first_attr_type()

        self.roles = self.roles or self.access_domain.role.select_related('parent').prefetch_related(
            'user_set__userinfo_set').all()
        if first_attr_type.attributeType == 'ou':
            if first_attr_type.value == 'user':
                for role in self.roles:
                    for user in role.user_set.all():
                        # for user in User.get_normal_user_list().prefetch_related('userinfo_set').filter(
                        #         role__in=self.roles).distinct():
                        data = self.access_domain.create_user(user)
                        dn = distinguishedname.DistinguishedName(
                            to_bytes('cn=%s,ou=user,%s' % (user.username, self.access_domain.basedn)))
                        user_dn = self.__class__(dn=dn)
                        user_dn.genrate_for_receive_data(data)
                        results.append(user_dn)
            elif first_attr_type.value == 'role':
                for role in self.roles:
                    data = self.access_domain.create_role(role)
                    dn = distinguishedname.DistinguishedName(
                        to_bytes('cn=%s,ou=role,%s' % (role.name, self.access_domain.basedn)))
                    role_dn = self.__class__(dn=dn)
                    role_dn.genrate_for_receive_data(data)
                    results.append(role_dn)
        if callback:
            for dn in results:
                callback(dn)

        return defer.succeed(results)

    def parent(self):
        if self.dn == '':
            # root
            return None
        else:
            parentPath, _ = os.path.split(self.path)
            return self.__class__(parentPath, self.dn.up())

    def is_root_dn(self):
        return self.get_dc_name() == self.get_first_attr_type().value

    def _sync_children(self):
        children = []
        first_attr_type = self.get_first_attr_type()

        if first_attr_type.attributeType == 'ou':
            self.roles = self.access_domain.role.select_related('parent').prefetch_related(
                'user_set__userinfo_set').all()
            if first_attr_type.value == 'user':
                for user in User.get_normal_user_list().prefetch_related('userinfo_set').filter(
                        role__in=self.roles).distinct():
                    # for role in self.roles:
                    #    for user in role.user_set.all():

                    if user.status != User.Status.NORMAL:
                        continue
                    data = self.access_domain.create_user(user)
                    dn = distinguishedname.DistinguishedName(
                        to_bytes('cn=%s,ou=user,%s' % (user.username, self.access_domain.basedn)))
                    user_dn = self.__class__(dn=dn)
                    user_dn.genrate_for_receive_data(data)
                    children.append(user_dn)
            elif first_attr_type.value == 'role':
                for role in self.roles:
                    data = self.access_domain.create_role(role)
                    dn = distinguishedname.DistinguishedName(
                        to_bytes('cn=%s,ou=role,%s' % (role.name, self.access_domain.basedn)))
                    role_dn = self.__class__(dn=dn)
                    role_dn.genrate_for_receive_data(data)
                    children.append(role_dn)
        return children

    def _children(self, callback=None):
        children = self._sync_children()
        if callback is None:
            return children
        else:
            for c in children:
                callback(c)
            return None

    def children(self, callback=None):
        return defer.maybeDeferred(self._children, callback=callback)

    def get_dc_name(self):
        dc_name = self.get_ldap_attr_type(self.dn.split()[-2]).value
        return dc_name

    def get_first_attr_type(self):
        return self.get_ldap_attr_type(self.dn.split()[0])

    def get_ldap_attr_type(self, relative_distinguished_name) -> distinguishedname.LDAPAttributeTypeAndValue:
        return relative_distinguished_name.split()[0]

    def lookup(self, dn):

        self.dn = distinguishedname.DistinguishedName(dn)
        self._load()

        if self.access_domain:
            return defer.succeed(self)
        else:
            return defer.fail(ldaperrors.LDAPNoSuchObject(dn.getText()))

    def _addChild(self, rdn, attributes):
        rdn = distinguishedname.RelativeDistinguishedName(rdn)
        for c in self._sync_children():
            if c.dn.split()[0] == rdn:
                raise ldaperrors.LDAPEntryAlreadyExists(c.dn.getText())

        dn = distinguishedname.DistinguishedName(
            listOfRDNs=(rdn,) + self.dn.split())
        e = entry.BaseLDAPEntry(dn, attributes)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        fileName = os.path.join(self.path, u'%s' % rdn.getText())
        tmp = u'%s.%s.tmp' % (fileName, str(uuid.uuid4()))
        f = open(tmp, 'wb')
        f.write(e.toWire())
        f.close()
        os.rename(tmp, fileName + u'.ldif')
        dirName = os.path.join(self.path, u'%s.dir' % rdn.getText())
        e = self.__class__(dirName, dn)
        return e

    def addChild(self, rdn, attributes):
        d = self._addChild(rdn, attributes)
        return d

    def _delete(self):
        if self.dn == '':
            raise LDAPCannotRemoveRootError()
        if self._sync_children():
            raise ldaperrors.LDAPNotAllowedOnNonLeaf(
                u'Cannot remove entry with children: %s' % self.dn.getText())
        assert self.path.endswith(u'.dir')
        entryPath = u'%s.ldif' % self.path[:-len(u'.dir')]
        os.remove(entryPath)
        return self

    def delete(self):
        return defer.maybeDeferred(self._delete)

    def _deleteChild(self, rdn):
        if not isinstance(rdn, distinguishedname.RelativeDistinguishedName):
            rdn = distinguishedname.RelativeDistinguishedName(stringValue=rdn)
        for c in self._sync_children():
            if c.dn.split()[0] == rdn:
                return c.delete()
        raise ldaperrors.LDAPNoSuchObject(rdn.getText())

    def deleteChild(self, rdn):
        return defer.maybeDeferred(self._deleteChild, rdn)

    def __repr__(self):
        return '%s( %r)' % (self.__class__.__name__,
                            self.dn.getText())

    def __lt__(self, other):
        if not isinstance(other, LDIFTreeEntry):
            # We don't return NotImplemented so that we get the same
            # result in Python2 and Python3.
            raise (TypeError, 'unorderable types: %r > %r' % (self, other))
        return self.dn < other.dn

    def __gt__(self, other):
        if not isinstance(other, LDIFTreeEntry):
            raise (TypeError, 'unorderable types: %r < %r' % (self, other))
        return self.dn > other.dn

    def commit(self):
        assert self.path.endswith(u'.dir')
        entryPath = self.path[:-len(u'.dir')]
        d = defer.maybeDeferred(_putEntry, entryPath, self)

        def eb_(err):
            from twisted.python import log
            log.msg("[ERROR] Could not commit entry: {0}.".format(self.dn))
            return False

        d.addErrback(eb_)
        return d

    def move(self, newDN):
        return defer.maybeDeferred(self._move, newDN)

    def _move(self, newDN):
        if not isinstance(newDN, distinguishedname.DistinguishedName):
            newDN = distinguishedname.DistinguishedName(stringValue=newDN)
        if newDN.up() != self.dn.up():
            # climb up the tree to root
            rootDN = self.dn
            rootPath = self.path
            while rootDN != '':
                rootDN = rootDN.up()
                rootPath = os.path.dirname(rootPath)
            root = self.__class__(path=rootPath, dn=rootDN)
            d = defer.maybeDeferred(root.lookup, newDN.up())
        else:
            d = defer.succeed(None)
        d.addCallback(self._move2, newDN)
        return d

    def _move2(self, newParent, newDN):
        # remove old RDN attributes
        for attr in self.dn.split()[0].split():
            self[attr.attributeType].remove(attr.value)
        # add new RDN attributes
        for attr in newDN.split()[0].split():
            self[attr.attributeType].add(attr.value)
        newRDN = newDN.split()[0]
        srcdir = os.path.dirname(self.path)
        if newParent is None:
            dstdir = srcdir
        else:
            dstdir = newParent.path

        newpath = os.path.join(dstdir, u'%s.dir' % newRDN.getText())
        try:
            os.rename(self.path, newpath)
        except OSError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise
        basename, ext = os.path.splitext(self.path)
        assert ext == u'.dir'
        os.rename(u'%s.ldif' % basename,
                  os.path.join(dstdir, u'%s.ldif' % newRDN.getText()))
        self.dn = newDN
        self.path = newpath
        return self.commit()
