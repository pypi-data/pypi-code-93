# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import ICheckBoxWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form import util
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import ITitledTokenizedTerm


class ILinkedCheckBoxWidget(ICheckBoxWidget):
    """Marker interface for Linked Checkbox Widget"""


@implementer_only(ILinkedCheckBoxWidget)
class LinkedCheckBoxWidget(CheckBoxWidget):

    @property
    def items(self):
        if self.terms is None:
            return ()

        registry = getUtility(IRegistry)
        urls = registry.get(self.links_record)

        items = []
        for term in self.terms:
            checked = self.isChecked(term)
            id = '%s-%s' % (self.id, term.value)
            if ITitledTokenizedTerm.providedBy(term):
                label = translate(term.title, context=self.request, default=term.title)
            else:
                label = util.toUnicode(term.value)
            items.append(
                {'id': id, 'name': self.name + ':list', 'value': term.token,
                 'label': label, 'checked': checked,
                 'url': urls.get(term.value).get('url')})
        return items

    @property
    def displayValue(self):
        registry = getUtility(IRegistry)
        urls = registry.get(self.links_record)

        value = []
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            try:
                term = self.terms.getTermByToken(token)
            except LookupError:
                # silently ignore missing tokens, because INPUT_MODE and
                # HIDDEN_MODE does that too
                continue
            title = term.value
            if ITitledTokenizedTerm.providedBy(term):
                title = translate(term.title, context=self.request, default=term.title)
            value.append({'term': title, 'url': urls.get(term.value).get('url'), 'class': 'sdg-{}'.format(token)})
        return value


@implementer(IFieldWidget)
def linked_checkbox_field_widget(field, request):
    return FieldWidget(field, LinkedCheckBoxWidget(request))
