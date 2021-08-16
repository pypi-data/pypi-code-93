from framework.models import BaseModel, models
from framework.translation import _

SyncModelMap = {'1': 'log_def.models.LogDefine', '2': 'analysis.models.query.Query', '3': 'log_def.models.DictDefine',
                '4': 'myadmin.models.menu.Menu',
                '5': 'analysis.models.statistic.Statistic', '6': 'flink_platform.models.CodeParagraph'}


class SyncModel(BaseModel):
    name = models.CharField(_('名称'), max_length=100, default='', null=False, blank=False)
    url = models.CharField(_('同步后台的地址'), max_length=200, default='', null=False, blank=False)
    key = models.CharField(default='', max_length=20, null=False, blank=True)
    is_old = models.BooleanField(default=False, null=False, blank=True)
    class Meta:
        ordering = ('id',)
