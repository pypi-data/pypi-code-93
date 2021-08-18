# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.
import os

from quartet_capture.models import Rule, Step, StepParameter
from quartet_templates.models import Template
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = _('Creates an example rule that shows how a response rule '
             'could be implemented.')

    def handle(self, *args, **options):
        db_rule = Rule.objects.create(
            name=_('SB Response Rule'),
            description=_('Will convert any inbound barcode data into URN '
                          'values and then apply a template to the values.')
        )
        list_step = Step.objects.create(
            name=_('List Conversion'),
            description=_('Will convert a list of barcode values to URNs.'),
            step_class='gs123.steps.ListBarcodeConversionStep',
            order=1,
            rule=db_rule
        )
        StepParameter.objects.create(
            step = list_step,
            name='Use Context Key',
            value='False'
        )
        template_step = Step.objects.create(
            name=_('Format Message'),
            description=_('Applies a QU4RTET template to the data within the'
                          ' rule.'),
            step_class='quartet_templates.steps.TemplateStep',
            order=2,
            rule=db_rule
        )
        ts_param = StepParameter.objects.create(
            name="Template Name",
            description="The name of the example template to use.",
            value="Example Response Template",
            step=template_step
        )
        file_data = self._get_file_data()
        template = Template.objects.create(
            name="Example Response Template",
            description="An example response template.",
            content = file_data
        )

    def _get_file_data(self):
        file_path = '../../tests/data/response_example.xml'
        curpath = os.path.dirname(__file__)
        f = open(os.path.join(curpath, file_path))
        return f.read()