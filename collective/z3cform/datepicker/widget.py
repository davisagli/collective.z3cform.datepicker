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
    
    showOn = u'both'
    buttonImage = u'popup_calendar.gif'
    buttonImageOnly = True
    onSelect = None
    altField = None
    altFormat = None

    def update(self):
        super(DatePickerWidget, self).update()
        widget.addFieldClass(self)
        
    def get_date_component(self, comp):
        """ Get string of of one part of datetime
        
        See z3c.form.converter.CalendarDataConverter
        
        @param comp: strftime formatter symbol
        """      
        
        locale = self.request.locale
        formatter = locale.dates.getFormatter("dateTime", "long")
                
        if self.value == u'':
            return None
        
        # Dug up the pattern with pdb, don't know where it comes from
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

    def datepicker_javascript(self):
        return '''
            jq(document).ready(function(){
                datepicker = jq("#%(id)s").datepicker({ 
                    %(onSelect)s%(altField)s%(altFormat)s
                    showOn: "%(showOn)s", 
                    buttonImage: "%(buttonImage)s", 
                    buttonImageOnly: %(buttonImageOnly)s
                });
                datepicker.attr("readonly", "readonly");
                datepicker.addClass('embed');
            });''' % dict(id                = self.id,
                          showOn            = self.showOn,
                          buttonImage       = self.buttonImage,
                          buttonImageOnly   = str(self.buttonImageOnly).lower(),
                          onSelect          = self.onSelect and 'onSelect: '+self.onSelect+',' or '',
                          altField          = self.altField and 'altField: "'+self.altField+'",' or '',
                          altFormat         = self.altFormat and 'altFormat: "'+self.altFormat+'",' or '')

class DateTimePickerWidget(DatePickerWidget):
    """ DateTime picker widget """
    implementsOnly(IDateTimePickerWidget)
   
    klass = u'datetimepicker-widget'
    value = u''

    years = range(1980, 2021)
    months = range(1, 13)
    days = range(1, 32)

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
        return '''
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
                                jq("#%(id)s-month").val(date[0]); 
                                jq("#%(id)s-day").val(date[1]); 
                                jq("#%(id)s-year").val(date[2]); 
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
                // Prevent selection of invalid dates through the select controls 
                function checkLinkedDays() { 
                    var daysInMonth = 32 - new Date(jq("#%(id)s-year").val(), 
                        jq("#%(id)s-month").val() - 1, 32).getDate(); 
                    jq("#%(id)s-day option").attr("disabled", ""); 
                    jq("#%(id)s-day option:gt(" + (daysInMonth - 1) +")").attr("disabled", "disabled"); 
                    if (jq("#%(id)s-day").val() > daysInMonth) { 
                        jq("#%(id)s-day").val(daysInMonth); 
                    } 
                }
                updateLinked(jq("#%(id)s").val());
                jq("#%(id)s-year").change(readLinked);
                jq("#%(id)s-month").change(readLinked);
                jq("#%(id)s-day").change(readLinked);
                jq("#%(id)s-hour").change(readLinked);
                jq("#%(id)s-min").change(readLinked);
                datepicker = jq("#%(id)s").datepicker({ 
                        minDate: new Date(2001, 1 - 1, 1),
                        maxDate: new Date(2010, 12 - 1, 31),
                        beforeShow: readLinked,
                        onSelect: updateLinked,
                        showOn: "%(showOn)s", 
                        buttonImage: "%(buttonImage)s", 
                        buttonImageOnly: %(buttonImageOnly)s
                });
                datepicker.attr("readonly", "readonly");
                jq("#%(id)s-month, #%(id)s-year").change(checkLinkedDays);
            });''' % dict(id                = self.id,
                          showOn            = self.showOn,
                          buttonImage       = self.buttonImage,
                          buttonImageOnly   = str(self.buttonImageOnly).lower())
            
                    
    def is_hour_checked(self, hour):
        """ <option> checket attribute evaluator """        
        return unicode(hour) == self.get_date_component("%H")

    def is_minute_checked(self, minute):
        """ <option> checket attribute evaluator """        
        # TODO what do to if minute drop down interval does not match the actual value
        return unicode(minute) == self.get_date_component("%M")


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
    length = 'long'

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

