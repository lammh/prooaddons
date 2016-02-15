# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from datetime import date,datetime
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp import SUPERUSER_ID
import datetime

from openerp.addons.wct_tools import amount_to_text


import logging
_logger = logging.getLogger(__name__)

class registration_recipt(report_sxw.rml_parse):


    def __init__(self, cr, uid, name, context=None):
        super(registration_recipt, self).__init__(cr, uid, name, context=context)
        from datetime import date,datetime,timedelta
        time = datetime.now()+timedelta(hours=1,minutes=00)
        self.localcontext.update({
            'time': time,
            'amount_to_text_tn': amount_to_text.amount_to_text_tn,
            'order_date' : self._get_order_date,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        data = []
        for id in ids:
            obj_registration_recipt = self.pool.get('pos.order')
            s = obj_registration_recipt.browse(self.cr, SUPERUSER_ID, id)
            s.nb_print = s.nb_print + 1
            print(s.nb_print)
            data.append(s)
        return super(registration_recipt, self).set_context(objects, data, ids, report_type)

    def _get_order_date(self, date):
        from datetime import timedelta
        date2=datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        datefi = date2 + timedelta(hours=1,minutes=00)
        return datefi


class report_registration_recipt(osv.AbstractModel):
    _name = 'report.oschool.report_registration_recipt'
    _inherit = 'report.abstract_report'
    _template = 'oschool.report_registration_recipt'
    _wrapped_report_class = registration_recipt

class report_timbre_recipt(osv.AbstractModel):
    _name = 'report.oschool.report_timbre_recipt'
    _inherit = 'report.abstract_report'
    _template = 'oschool.report_timbre_recipt'
    _wrapped_report_class = registration_recipt

class report_no_timbre_recipt(osv.AbstractModel):
    _name = 'report.oschool.report_no_timbre_recipt'
    _inherit = 'report.abstract_report'
    _template = 'oschool.report_no_timbre_recipt'
    _wrapped_report_class = registration_recipt



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: