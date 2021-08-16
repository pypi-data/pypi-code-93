# coding:utf-8
# 创建增删改查页面


import datetime
import os
import os.path

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models.fields.related import ForeignKey
from django.forms import ModelForm
from mako.lookup import TemplateLookup

from framework.filters import MyFilterBackend
from framework.models import BaseModel, BaseModelMixin
from framework.route import reverse_view
from ...utils import mkdirs, ObjectDict


class ModelTemplateCreater(object):
    def __init__(self, app_name, model_name, model, params={}, options={}):
        self.model = model
        self.app_name = app_name
        self.model_name = model_name
        self.model_lower_name = model.get_lower_name()
        self.is_force = options.get('force', False)
        self.params = params
        self.params['model'] = self.model
        self.params['model_name'] = self.model_name
        self.params['model_lower_name'] = self.model_lower_name
        self.options = options
        self.tpl_dir = options.get('tpl_dir') or 'curd_tpl'

    def get_app_path(self):
        return apps.app_configs.get(self.app_name).path

    def get_app_tempalte_path(self):
        return os.path.join(self.get_app_path(),'jinja2_templates')

    @property
    def template_dir(self):

        code_tpl_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..', 'code_tpl', self.tpl_dir))
        print(code_tpl_dir)
        return code_tpl_dir

    def create_edit_t_file(self):
        template_file = 'model_edit.htm'
        target_file = os.path.join(self.get_app_tempalte_path(), self.app_name, self.model_lower_name, 'edit.html')
        self._create_base_file(template_file, target_file)

    def create_list_t_file(self):
        template_file = 'model_list.htm'
        target_file = os.path.join(self.get_app_tempalte_path(), self.app_name, self.model_lower_name, 'list.html')
        self._create_base_file(template_file, target_file)

    def create_model_v_file(self):
        template_file = 'view.py.tpl'
        single_view_file = os.path.join(self.get_app_path(), 'views.py')
        if os.path.isfile(single_view_file):
            target_file = single_view_file
        else:
            target_file = os.path.join(self.get_app_path(), 'views', '%s.py' % self.model_lower_name)
        self._create_base_file(template_file, target_file)

    def create_files(self):
        if self.is_force or self.options.get('view', False):
            self.create_model_v_file()
        if self.options.get('tpl', False) or self.is_force or self.options.get('edit', False):
            self.create_edit_t_file()
        if self.options.get('tpl', False) or self.is_force or self.options.get('list', False):
            self.create_list_t_file()

    def _create_base_file(self, template_file, target_file):
        mylookup = TemplateLookup(directories=[self.template_dir], input_encoding='utf-8', output_encoding='utf-8')
        template = mylookup.get_template(template_file)
        template_str = template.render(**self.params)

        mkdirs(os.path.dirname(target_file))

        # bak_file = '%s_bak' % target_file
        #
        # if not os.path.isfile(bak_file) and os.path.isfile(target_file):
        #     with open('%s_bak' % target_file, 'wb') as back_file:
        #         with open(target_file, 'rb') as f:
        #             back_file.write(f.read())

        with open(target_file, 'wb') as f:
            f.write(template_str)

        print('create %s ok !' % target_file)


class Command(BaseCommand):
    '''创建 curd 增删改查 默认模板命令行
    '''
    help = '创建MTV模型命令,%s app_name.model' % __file__

    def add_arguments(self, parser):

        parser.add_argument('-f', '--force', action='store_true',
                            dest='force', default=False,
                            help='强制创建')
        parser.add_argument('-t', '--tpl', action='store_true',
                            dest='tpl', default=False,
                            help='只创建模版')

        parser.add_argument('-vi', '--view', action='store_true',
                            dest='view', default=False,
                            help='只创建 view 视图 模版')

        parser.add_argument('-e', '--edit', action='store_true',
                            dest='edit', default=False,
                            help='只创建 edit 模版')
        parser.add_argument('-l', '--list', action='store_true',
                            dest='list', default=False,
                            help='只创建 list 模版')
        parser.add_argument(
                "--model_file", "-mf", dest="model_file_path", default='',
                help="指定 model 文件路径"
        )
        parser.add_argument(
                "--tpl_dir", "-td", dest="tpl_dir", default='',
                help="指定 curd 模板目录"
        )

        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        force = options.get('force', False)
        model_file_path = options.get('model_file_path')

        if len(args) < 1:
            self.stderr.write('请输入模型名,注意大小写')
            return

        if model_file_path:
            model_module_path = model_file_path.replace(os.sep, '.').rstrip('.py')
            model_name = args[0]
            app_name = model_module_path.split('.')[0]
            model_import_path = model_module_path
        else:
            app_name_model_name = args[0]
            app_name, model_name = app_name_model_name.split('.')
            model_import_path = '%s.models' % app_name

        models = __import__(model_import_path, fromlist=(app_name,))

        model_class: BaseModel = getattr(models, model_name)

        if not issubclass(model_class, BaseModelMixin):
            #raise Exception('不是继承于 BaseModel' )
            model_class._meta.abstract=True
            model_class = type(
                    model_class.__name__,
                    (model_class,BaseModelMixin),
                    {'__module__': model_class.__module__,'__doc__': model_class.__name__}
            )
        if not model_class:
            self.stderr.write('%s 模型载入失败' % model_name)
            return
        # 动态构造一个 model_form

        model_form_class = type("%sForm" % model_name, (ModelForm,),
                                {"Meta": type("Meta", (object,), {"model": model_class, "exclude": ()})})
        model_form = model_form_class({})
        parmas = {}
        base_field_names = ['create_datetime', 'update_datetime']
        fields = []
        base_fields = []
        _fields = model_class.get_fields()

        filter_field_operator = {}
        filter_field_schemas = []

        for field in _fields:
            if field.name in base_field_names:

                base_fields.append(field)
            else:
                fields.append(field)
        fields += base_fields
        for field in fields:
            filed_operator = MyFilterBackend.get_operator_enum(field)
            filter_field_operator[field] = filed_operator
            field_schema = ObjectDict()
            field_schema.name = field.name
            field_schema.label = field.verbose_name
            field_schema.type = filed_operator.value
            # field_schema.data_url = field.related_model().get_list_url() if field.related_model else ''

            field_schema.data_url = reverse_view(
                    '%s.%s.list' % (app_name, model_class.get_lower_name())) if field.related_model else ''

            field_schema.choices = getattr(field, 'choices', [])
            filter_field_schemas.append(field_schema)

        parmas['filter_filed_operator'] = filter_field_operator
        parmas['filter_field_schemas'] = filter_field_schemas

        parmas['app_name'] = app_name
        parmas['model'] = model_class
        parmas['model_form'] = model_form

        parmas['model_many_to_many'] = model_class._meta.many_to_many
        parmas['model_foreigns'] = [f for f in _fields if isinstance(f, ForeignKey)]
        parmas['model_choices_fields'] = [f for f in _fields if f.choices]
        parmas['model_desc'] = model_class.__doc__.strip().split('\n')[0] or model_name

        parmas['fields_name_list'] = [f.name for f in fields]
        parmas['all_fields_name_list'] = parmas['fields_name_list'] + ['%s_alias' % f.name for f in
                                                                       parmas['model_choices_fields']]
        parmas['fields'] = fields
        parmas['datetime'] = datetime.datetime.now()

        print('create_files')
        print((model_class, parmas['model_desc']))
        ModelTemplateCreater(app_name, model_name, model_class, parmas, options).create_files()
