
from zope.interface import Interface
from zope.schema import Date
from zope.schema import Datetime

from z3c.form.form import Form
from z3c.form.field import Fields
from z3c.form.button import buttonAndHandler
from z3c.form.interfaces import INPUT_MODE
from plone.app.z3cform.layout import wrap_form
from collective.z3cform.datepicker.widget import DatePickerFieldWidget
from collective.z3cform.datepicker.widget import DateTimePickerFieldWidget


class ITestForm(Interface):
    """ """
    date = Date(
        title       = u'Date widget',
        required    = False,)
    datetime = Datetime(
        title       = u'DateTime widget',
        required    = False,)


class TestForm(Form):
    """ """

    ignoreContext = True
    fields = Fields(ITestForm)
    fields['date'].widgetFactory[INPUT_MODE] = DatePickerFieldWidget
    fields['datetime'].widgetFactory[INPUT_MODE] = DateTimePickerFieldWidget

    @buttonAndHandler(u'Submit')
    def submit(self, action):
        data, errors = self.extractData()
        if errors: return False
        return True

TestView = wrap_form(TestForm)
