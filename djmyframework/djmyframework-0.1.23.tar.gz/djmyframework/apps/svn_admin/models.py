# Create your models here.
import configparser
import json
import os
import shutil

from framework.models import BaseModel, JSONField, models
from framework.translation import _
from framework.utils import mkdirs
from framework.utils.myenum import Enum
from framework.utils import encrypt
from framework.validators import LetterValidator
from myadmin.models import User
from .settings import SVN_AUTH_DB_FILE, SVN_GROUP_DB_FILE, SVN_PASSWORD_DB_FILE, SVN_ROOT


class SvnUser(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_password = models.CharField(max_length=128, null=False, default='')

    def set_raw_password(self,password_text):
        self.raw_password = encrypt.encrypt(password_text)

    def get_raw_password(self):
        return encrypt.decrypt(self.raw_password)

class SvnPath(BaseModel):
    """
    SVN 路径
    """

    class Status(Enum):
        Enable = 0, _('开启')
        Disable = 1, _('关闭')

    class Permission(Enum):
        Read = 'r', _('只读')
        Write = 'w', _('只写')
        ReadWrite = 'rw', _('可读写')
        Empty = 'no', _('禁止访问')

    project_name = models.CharField(max_length=100, verbose_name=_('项目名'), db_index=True, null=False, blank=False,
                                    validators=[LetterValidator])
    alias = models.CharField(max_length=200, verbose_name=_('项目别称'), default='', null=False, blank=True)

    path = models.CharField(max_length=200, verbose_name=_('svn 路径'), db_index=True, null=False, blank=False)

    parent = models.ForeignKey(to='self', verbose_name=_('上级路径'), null=True, on_delete=models.DO_NOTHING, blank=True)

    status = models.IntegerField(verbose_name=_('状态'), choices=Status.member_list(), default=Status.Enable, null=True,
                                 blank=True)
    remark = models.CharField(max_length=500, verbose_name=_('备注'), default='', null=False, blank=True)
    read_member = JSONField(verbose_name=_('可读成员'), default='[]', blank=True, null=False)
    write_member = JSONField(verbose_name=_('可写成员'), default='[]', blank=True, null=False)
    other_permission = models.CharField(verbose_name=_('其他访问权限'), max_length=2, choices=Permission.member_list(),
                                        default=Permission.Empty, null=False, blank=True)

    class Meta:
        ordering = ['id']
        unique_together = (('project_name', 'path'))

    def save(self, *args, **kwargs):
        if self.path != '/':
            self.parent = self.__class__.objects.get(project_name=self.project_name, parent=None, path='/')
            self.path = self.path.strip('/')

        r = super(SvnPath, self).save(*args, **kwargs)
        SvnPath.sync_svn_config_file()
        return r

    svn_root_conf_path = os.path.join(SVN_ROOT, 'conf')

    @classmethod
    def create_conf(cls):
        default_svnserve_conf_text = '''
### Visit http://subversion.apache.org/ for more information.
[general]
anon-access = none
auth-access = write
password-db = {password_db}
authz-db = {authz_db}
groups-db = {groups_db}
# realm = My First Repository
# force-username-case = none
# hooks-env = hooks-env

[sasl]
# use-sasl = true
# min-encryption = 0
# max-encryption = 256
        '''
        mkdirs(cls.svn_root_conf_path)
        svnserve_conf_file = os.path.join(cls.svn_root_conf_path, 'svnserve.conf')
        if not os.path.isfile(svnserve_conf_file):
            open(svnserve_conf_file, 'w').write(
                    default_svnserve_conf_text.format(password_db=SVN_PASSWORD_DB_FILE, authz_db=SVN_AUTH_DB_FILE,
                                                      groups_db=SVN_GROUP_DB_FILE))

    @classmethod
    def create_svnrepo(cls, svnrepo_name):
        cls.create_conf()
        svnrepo_path = os.path.join(SVN_ROOT, svnrepo_name)
        svnrepo_conf_path = os.path.join(svnrepo_path, 'conf')
        if not os.path.isdir(svnrepo_path):
            os.system('svnadmin create %s' % svnrepo_path)
        if not os.path.islink(svnrepo_conf_path):
            shutil.rmtree(svnrepo_conf_path)
            os.symlink(cls.svn_root_conf_path, svnrepo_conf_path)

    @property
    def section_name(self):
        return '{project_name}:{path}'.format(project_name=self.project_name,
                                              path=self.full_path)

    @property
    def full_path(self):
        return '/' + self.path.strip('/')

    @classmethod
    def get_password_db(self):
        password_db = configparser.ConfigParser()
        password_db.read(SVN_PASSWORD_DB_FILE)
        return password_db

    @classmethod
    def get_authz_db(self):
        authz_db = configparser.ConfigParser()
        authz_db.read(SVN_AUTH_DB_FILE)
        return authz_db

    @classmethod
    def get_groups_db(self):
        authz_db = configparser.ConfigParser()
        authz_db.read(SVN_GROUP_DB_FILE)
        return authz_db

    @classmethod
    def sync_svn_config_file(cls):
        cls.sync_user_to_password_db()
        cls.sync_group_menber_to_authz_db()
        cls.sync_svn_path_authz_db()

    USER_SECTION_NAME = 'users'
    GROUP_SECTION_NAME = 'groups'

    user_set = set()
    group_set = set()

    @classmethod
    def get_svn_project_list(cls):
        from .settings import SVN_ROOT
        dirs = os.listdir(SVN_ROOT)
        project_list = []
        for d in dirs:
            if os.path.isfile(os.path.join(SVN_ROOT, d, 'format')):
                project_list.append(d)
        return project_list

    @classmethod
    def get_tree_list(cls, project_name, list_path='/'):
        project_path = os.path.join(SVN_ROOT, project_name)
        cmd = 'svnlook tree -N --full-paths {project_path} {list_path} '.format(project_path=project_path,
                                                                                  list_path=list_path)
        result = {project_name: []}
        for path in os.popen(cmd).readlines():
            path = path.strip()
            if path and path[-1] == '/' and path!=list_path:
                result[project_name].append(path)
        return result

    @classmethod
    def init_svn_projects(cls):
        project_list = cls.get_svn_project_list()
        for project_name in project_list:
            svn_paht_model = cls.objects.get_or_create(project_name=project_name, parent=None, path='/')
            # svn_paht_model.parent = None
            # svn_paht_model.save()

    @classmethod
    def sync_user_to_password_db(cls):
        password_db = cls.get_password_db()
        password_db.clear()
        user_section_name = cls.USER_SECTION_NAME
        if not password_db.has_section(user_section_name):
            password_db.add_section(user_section_name)

        cls.user_set.clear()
        for svnuser in SvnUser.objects.select_related('user').all():
            user = svnuser.user
            password_db.set(user_section_name, user.username, svnuser.get_raw_password())
            cls.user_set.add(user.username)
        password_db.write(open(SVN_PASSWORD_DB_FILE, "w"))

    @classmethod
    def sync_group_menber_to_authz_db(cls):
        groups_db = cls.get_groups_db()
        group_section_name = cls.GROUP_SECTION_NAME
        if not groups_db.has_section(group_section_name):
            groups_db.add_section(group_section_name)

        cls.group_set.clear()
        for role in Role.objects.prefetch_related('user_set').filter(type=Role.RoleType.GROUP):
            user_name_list = role.user_set.values_list('username', flat=True)
            if user_name_list:
                cls.group_set.add('@%s' % role.name)
                groups_db.set(group_section_name, role.name, ','.join(user_name_list))
        groups_db.write(open(SVN_GROUP_DB_FILE, "w"))

    @classmethod
    def sync_svn_path_authz_db(cls):
        authz_db = cls.get_authz_db()
        authz_db.clear()

        for svn_path_model in cls.objects.filter(status=cls.Status.Enable):
            svn_path_section_name = svn_path_model.section_name

            if authz_db.has_section(svn_path_section_name):
                authz_db.remove_section(svn_path_section_name)
            authz_db.add_section(svn_path_section_name)
            allow_menber = cls.user_set | cls.group_set
            read_member_set = set(json.loads(svn_path_model.read_member)) & allow_menber
            write_member_set = set(json.loads(svn_path_model.write_member)) & allow_menber
            rw_list = read_member_set & write_member_set

            for member in rw_list:
                authz_db.set(svn_path_section_name, member, 'rw')

            for member in read_member_set - rw_list:
                authz_db.set(svn_path_section_name, member, 'r')
            for member in write_member_set - rw_list:
                authz_db.set(svn_path_section_name, member, 'w')
            authz_db.set(svn_path_section_name, '*',
                         '' if svn_path_model.other_permission == cls.Permission.Empty else svn_path_model.other_permission)

        authz_db.write(open(SVN_AUTH_DB_FILE, "w"))


from django.db.models.signals import post_delete, post_save, m2m_changed
from django.dispatch import receiver
from myadmin.models import User, Role


@receiver(post_save, sender=User, dispatch_uid="user_save_svn")
def user_save_svn(sender, instance, **kwargs):
    user: User = instance
    password_db = SvnPath.get_password_db()
    user_section_name = SvnPath.USER_SECTION_NAME
    if not password_db.has_section(user_section_name):
        password_db.add_section(user_section_name)

    if user.status == User.Status.NORMAL:
        if user._password is not None:
            svn_user_model, _ = SvnUser.objects.get_or_create(user=user)
            svn_user_model.set_raw_password(user._password)
            svn_user_model.save()
            password_db.set(user_section_name, user.username, svn_user_model.get_raw_password())
            password_db.write(open(SVN_PASSWORD_DB_FILE, "w"))
    else:
        user_delete_svn(sender, instance)


@receiver(post_delete, sender=User, dispatch_uid="user_delete_svn")
def user_delete_svn(sender, instance, **kwargs):
    user: User = instance
    password_db = SvnPath.get_password_db()
    if password_db.has_option(SvnPath.USER_SECTION_NAME, user.username):
        password_db.remove_option(SvnPath.USER_SECTION_NAME, user.username)
    password_db.write(open(SVN_PASSWORD_DB_FILE, "w"))


@receiver(m2m_changed, sender=User.role.through, dispatch_uid="user_add_role_ldap")
def user_add_role_ldap(sender, action, instance: Role, reverse, model: User, pk_set, using, **kwargs):
    if action in ['post_add', 'post_clear', 'post_remove']:
        SvnPath.sync_group_menber_to_authz_db()
