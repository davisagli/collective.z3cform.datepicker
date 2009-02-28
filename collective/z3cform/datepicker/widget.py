#-*- coding: utf-8 -*- 

#############################################################################
#                                                                           #
#   Copyright (c) 2008 Rok Garbas <rok.garbas@gmail.com>                    #
#                                                                           #
# This program is free software; you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation; either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################


from DateTime import DateTime
from zope.component import adapts
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.app.form.interfaces import ConversionError
from zope.app.i18n import ZopeMessageFactory as _
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.i18n.format import DateTimeParseError
from zope.i18n.interfaces import IUserPreferredLanguages

import z3c.form
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.converter import CalendarDataConverter
from z3c.form.converter import FormatterValidationError

from collective.z3cform.datepicker.interfaces import IDatePickerWidget
from collective.z3cform.datepicker.interfaces import IDateTimePickerWidget


class DatePickerWidget(widget.HTMLTextInputWidget, Widget):
    """ Datepicker widget. """
    implementsOnly(IDatePickerWidget)

    klass = u'datepicker-widget'
    size = 30 # we need a little bigger input box

    # 
    # for explanation how to set options look at:
    # http://docs.jquery.com/UI/Datepicker
   
    options = dict(
        # altField - we dont alow to change altField since we use it in our widget
        altFormat               = u'DD, d MM, yy',
        # appendText - we provide description different way
        beforeShow              = None,
        beforeShowDay           = None,
        buttonImage             = u'popup_calendar.gif',
        buttonImageOnly         = True,
        buttonText              = u'...',
        calculateWeek           = u'$.datepicker.iso8601Week',
        changeFirstDay          = True,
        changeMonth             = True,
        changeYear              = True,
        closeText               = u'Close',
        constrainInput          = True,
        currentText             = u'Today',
        # dateFormat - we use mm/dd/yy always
        dayNames                = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                                   'Thursday', 'Friday', 'Saturday'],
        dayNamesMin             = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
        dayNamesShort           = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        defaultDate             = None,
        duration                = u'normal',
        firstDay                = 0,
        gotoCurrent             = False,
        hideIfNoPrevNext        = False,
        isRTL                   = False,
        maxDate                 = None,
        minDate                 = None,
        monthNames              = ['January', 'February', 'March', 'April', 'May',
                                   'June', 'July', 'August', 'September',
                                   'October', 'November', 'DecenextTextmber'],
        monthNamesShort         = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        navigationAsDateFormat  = False,
        nextText                = u'Next>',
        numberOfMonths          = 1,
        prevText                = u'<Prev',
        shortYearCutoff         = 10,
        showAnim                = u'show',
        showButtonPanel         = False,
        showOn                  = u'both',
        showOptions             = {},
        showOtherMonths         = False,
        stepMonths              = 1,
        yearRange               = u'-10:+10')

    events = dict(
        onChangeMonthYear       = None,
        onClose                 = None,
        onSelect                = None)

    @property
    def _options(self):
        return dict(
        altField   = '#'+self.id+u'-for-display',
        dateFormat = u'mm/dd/yy')

    def update(self):
        super(DatePickerWidget, self).update()
        widget.addFieldClass(self)

    @property
    def language(self):
        return IUserPreferredLanguages(self.request).getPreferredLanguages()[0]

    def compile_options(self):
        options = ''
        for name, value in self._options.items()+self.options.items():
            if value == None: value = 'null'
            elif type(value) == bool: value = str(value).lower()
            elif type(value) in [list, dict, int]: value = str(value)
            elif name in ['beforeShow','beforeShowDay','minDate','maxDate']: value = str(value)
            else: value = '"'+str(value)+'"'
            options += name+': '+str(value)+','
        for name, value in self.events.items():
            if not value: continue
            options += name+': '+str(value)+','
        return options[:-1]

    def datepicker_javascript(self):
        return '''/* <![CDATA[ */
            jq(document).ready(function(){
                datepicker = jq("#%(id)s").datepicker({%(options)s});
                jq("%(altField)s").attr("readonly", "readonly");
                jq("%(altField)s").addClass('embed');
                jq("%(altField)s").each(function() {
                    jq(this).val(jq.datepicker.formatDate("%(altFormat)s",
                        jq("#%(id)s").datepicker('getDate'),
                        {shortYearCutoff: %(shortYearCutoff)s,
                         dayNamesShort: %(dayNamesShort)s,
                         dayNames: %(dayNames)s,
                         monthNamesShort: %(monthNamesShort)s,
                         monthNames: %(monthNames)s}
                    ));
                });
                jq("#%(id)s-clear").click(function() { 
                    jq("#%(id)s").val('');
                    jq("%(altField)s").val('');
                });
            });
            /* ]]> */''' % dict(id=self.id,
                                options=self.compile_options(),
                                altField=self._options['altField'],
                                altFormat=self.options['altFormat'],
                                shortYearCutoff=self.options['shortYearCutoff'],
                                dayNamesShort=self.options['dayNamesShort'],
                                dayNames=self.options['dayNames'],
                                monthNamesShort=self.options['monthNamesShort'],
                                monthNames=self.options['monthNames'])

class DateTimePickerWidget(DatePickerWidget):
    """ DateTime picker widget """
    implementsOnly(IDateTimePickerWidget)
   
    klass = u'datetimepicker-widget'
    value = u''
    
    years = range(1980, 2021)
    months = range(1, 13)
    days = range(1, 32)
    
    options = DatePickerWidget.options.copy()
    options.update(dict(beforeShow='readLinked',
                        yearRange=str(years[0])+':'+str(years[-1])))
    events = DatePickerWidget.events.copy()
    events.update(dict(onSelect='updateLinked'))
    _options = dict(dateFormat='mm/dd/yy')
    
    @property
    def hours(self):
        hours = []
        for i in range(0, 24):
            if i<10:
                hours.append('0'+str(i))
            else:
                hours.append(str(i))
        return hours

    @property
    def minutes(self):
        minutes = []
        for i in range(0, 60, 5):
            if i<10:
                minutes.append('0'+str(i))
            else:
                minutes.append(str(i))
        return minutes

    def datepicker_javascript(self):
        return '''/* <![CDATA[ */
            jq(document).ready(function(){
                // Prepare to show a date picker linked to three select controls 
                function readLinked() { 
                    jq("#%(id)s").val(jq("#%(id)s-month").val()+'/'+
                                      jq("#%(id)s-day").val()+'/'+
                                      jq("#%(id)s-year").val()+' '+
                                      jq("#%(id)s-hour").val()+':'+
                                      jq("#%(id)s-min").val());
                    return {}; 
                } 
                // Update three select controls to match a date picker selection 
                function updateLinked(date) { 
                    if (date != '') {
                        var datetime = date.split(" ");
                        if (datetime.length==1) {
                            date = datetime[0].split('/');
                            if (date.length==3) {
                                jq("#%(id)s-month").val(parseInt(date[0])); 
                                jq("#%(id)s-day").val(parseInt(date[1])); 
                                jq("#%(id)s-year").val(parseInt(date[2])); 
                            }
                        }
                        if (datetime.length==2) {
                            date = datetime[0].split('/');
                            var time = datetime[1].split(':');
                            if (date.length==3&&time.length==2) {
                                jq("#%(id)s-month").val(date[0]); 
                                jq("#%(id)s-day").val(date[1]); 
                                jq("#%(id)s-year").val(date[2]); 
                                jq("#%(id)s-hour").val(time[0]); 
                                jq("#%(id)s-min").val(time[1]); 
                            } 
                        }
                    }
                    readLinked();
                } 
                updateLinked(jq("#%(id)s").val());
                jq("#%(id)s-year").change(readLinked);
                jq("#%(id)s-month").change(readLinked);
                jq("#%(id)s-day").change(readLinked);
                jq("#%(id)s-hour").change(readLinked);
                jq("#%(id)s-min").change(readLinked);

                datepicker = jq("#%(id)s").datepicker({%(options)s});
                // Prevent selection of invalid dates through the select controls 
                jq("#%(id)s-month, #%(id)s-year").change(function () { 
                    var daysInMonth = 32 - new Date(jq("#%(id)s-year").val(), 
                        jq("#%(id)s-month").val() - 1, 32).getDate(); 
                    jq("#%(id)s-day option").attr("disabled", ""); 
                    jq("#%(id)s-day option:gt(" + (daysInMonth - 1) +")").attr("disabled", "disabled"); 
                    if (jq("#%(id)s-day").val() > daysInMonth) { 
                        jq("#%(id)s-day").val(daysInMonth); 
                    } 
                });
            });
            /* ]]> */''' % dict(id=self.id,options=self.compile_options())
                    
    def get_date_component(self, comp):
        """ Get string of of one part of datetime.
        
        See z3c.form.converter.CalendarDataConverter
        
        @param comp: strftime formatter symbol
        """      
    
        # match z3c.form.converter here
        locale = self.request.locale
        formatter = locale.dates.getFormatter("dateTime", "long")
        
        if self.value == u'':
            return None

        try:
            value = formatter.parse(self.value)
        except:
            #import pdb ; pdb.set_trace()
            return None
        
        # TODO: What if the strftime return value has international letters?
        return unicode(value.strftime(comp))
        
    def is_month_checked(self, month):
        """ <option> checket attribute evaluator """
        
        value = self.get_date_component("%m")
        # Strip leading zero
        if value == None:
            return False
        value = int(str(value))
        
        return unicode(month) == unicode(value)

    def is_day_checked(self, day):
        """ <option> checket attribute evaluator """        
        return unicode(day) == self.get_date_component("%d")
        
    def is_year_checked(self, year):
        """ <option> checket attribute evaluator """
        return unicode(year) == self.get_date_component("%Y")

    def is_hour_checked(self, hour):
        """ <option> checket attribute evaluator """        
        return unicode(hour) == self.get_date_component("%H")

    def is_minute_checked(self, minute):
        """ <option> checket attribute evaluator """        
        # TODO what do to if minute drop down interval does not match the actual value
        return unicode(minute) == self.get_date_component("%M")
    
    def extract(self, default=z3c.form.interfaces.NOVALUE):
        """ Non-Javascript based value reader.
        
        Scan all selection lists and form datetime based on them.
        """
        
        components = [ "year", "day", "month", "hour", "min" ]
        values = {}
        
        for c in components:
            # Get individual selection list value
            
            # name is in format form.widgets.acuteInterventions_actilyseTreatmentDate
            
            component_value = self.request.get(self.name + "-" + c, default)
            if component_value == default:
                # One component missing, 
                # cannot built datetime
                return default
            
            values[c] = component_value
     
        # convert to datepicker internal format
        # TODO: Check this is fixed and not tied to portal_properties
        return "%s/%s/%s %s:%s" % (values["month"], values["day"], values["year"], values["hour"], values["min"])


@adapter(IDatePickerWidget, IFormLayer)
@implementer(IFieldWidget)
def DatePickerFieldWidget(field, request):
   """IFieldWidget factory for DatePickerFieldWidget."""
   return FieldWidget(field, DatePickerWidget(request))

@adapter(IDateTimePickerWidget, IFormLayer)
@implementer(IFieldWidget)
def DateTimePickerFieldWidget(field, request):
   """IFieldWidget factory for DateTimePickerFieldWidget."""
   return FieldWidget(field, DateTimePickerWidget(request))


class DateTimeConverter(CalendarDataConverter):
    """A special data converter for datetimes."""

    adapts(IDatetime, IDateTimePickerWidget)
    type = 'dateTime'

    def toFieldValue(self, value):
        """See interfaces.IDataConverter""" 
        if value == u'':
            return self.field.missing_value
        try:
            return self.formatter.parse(value, pattern="M/d/yyyy H:m")
        except DateTimeParseError, err:
            raise FormatterValidationError(err.args[0], value)

class DateConverter(CalendarDataConverter):
    """A special data converter for datetimes."""

    adapts(IDate, IDatePickerWidget)
    type = 'date'

    def toFieldValue(self, value):
        """See interfaces.IDataConverter""" 
        if value == u'':
            return self.field.missing_value
        try:
            return self.formatter.parse(value, pattern="M/d/yyyy")
        except DateTimeParseError, err:
            raise FormatterValidationError(err.args[0], value)

