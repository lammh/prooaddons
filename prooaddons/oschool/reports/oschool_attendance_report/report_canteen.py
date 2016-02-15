# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp import SUPERUSER_ID
from datetime import datetime, timedelta


import logging
_logger = logging.getLogger(__name__)

class canteen(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(canteen, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

    def set_context(self, objects, data, ids, report_type=None):
        obj_canteen = self.pool.get('oschool.canteen.wizard')
        c = obj_canteen.browse(self.cr, SUPERUSER_ID, ids)
        first_day = datetime.strptime(c.period_id.date_start, "%Y-%m-%d")
        res = []
        while first_day <= datetime.strptime(c.period_id.date_stop, "%Y-%m-%d"):
            d = datetime.strftime(first_day, "%a%d")
            if (first_day.weekday() != 5) and (first_day.weekday() != 6):
                res.append(d)
            first_day += timedelta(days=1)

        data = {}
        data['canteen'] = c
        data['res'] = res
        return super(canteen, self).set_context(objects, data, ids, report_type)

class report_canteen(osv.AbstractModel):
    _name = 'report.oschool.report_canteen'
    _inherit = 'report.abstract_report'
    _template = 'oschool.report_canteen'
    _wrapped_report_class = canteen




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: