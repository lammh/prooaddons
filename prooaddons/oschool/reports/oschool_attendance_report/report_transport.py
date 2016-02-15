# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp import SUPERUSER_ID
from datetime import datetime, timedelta


import logging
_logger = logging.getLogger(__name__)

class transport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(transport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

    def set_context(self, objects, data, ids, report_type=None):
        obj_transport = self.pool.get('oschool.transport.wizard')
        obj_driver_hostess = self.pool.get('oschool.driver_hostess_assignment')
        trans = obj_transport.browse(self.cr, SUPERUSER_ID, ids)
        data={}
        date_strat = datetime.strptime(trans.period_id.date_start, "%Y-%m-%d")
        date_stop = datetime.strptime(trans.period_id.date_stop, "%Y-%m-%d")
        data['periods'] = []

        week = timedelta(days=7)
        while (date_strat < date_stop):
            id = obj_driver_hostess.search(self.cr, SUPERUSER_ID, [
                ('bus_to_zone_id.zone.id','=',trans.zone_id.id),
                ('day','=',datetime.strftime(date_strat, "%Y-%m-%d"))
            ])
            res = {}
            res['driver'] = ""
            res['hostess'] = ""
            if id:
                res['driver'] = obj_driver_hostess.browse(self.cr, SUPERUSER_ID, id[0]).driver.name
                res['hostess'] = obj_driver_hostess.browse(self.cr, SUPERUSER_ID, id[0]).hostess.name
            res['date_start'] = datetime.strftime(date_strat, "%d-%m-%Y")
            date_strat = (date_strat + week)
            res['date_stop'] = datetime.strftime(date_strat, "%d-%m-%Y")
            data['periods'].append(res)
        pres = {}
        for presnce in trans.presence_ids:
            if not int(presnce.group_id.seq) in pres :
                pres[int(presnce.group_id.seq)] = {}
                pres[int(presnce.group_id.seq)]['group'] = presnce.group_id
                pres[int(presnce.group_id.seq)]['presence'] = []
            pres[int(presnce.group_id.seq)]['presence'].append(presnce)
            keylist = pres.keys()
            keylist.sort()
            p =[]
            for key in keylist:
                p.append(pres[key])

        data['zone'] = trans.zone_id.name
        data['presence'] = []
        for presence in p:
            data['presence'].append(presence)

        return super(transport, self).set_context(objects, data, ids, report_type)

class report_transport(osv.AbstractModel):
    _name = 'report.oschool.report_transport'
    _inherit = 'report.abstract_report'
    _template = 'oschool.report_transport'
    _wrapped_report_class = transport




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: