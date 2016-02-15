# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, CRM Repair Report Extension
#    Copyright (C) 2014  Enterprise Objects Consulting
#
#    Authors: Mariano Ruiz <mrsarm@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp.tools.translate import _

from openerp.addons.crm.crm import AVAILABLE_PRIORITIES

try:
    from openerp.addons.crm_claim_picking.crm_claim import AVAILABLE_ACTIONS
except:
    AVAILABLE_ACTIONS = [
            ('correction','Corrective Action'),
            ('prevention','Preventive Action'),
        ]



class crm_claim(report_sxw.rml_parse):
    _name = 'report.crm.claim'

    def __init__(self, cr, uid, name, context):
        super(crm_claim, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_prio': self._get_priority,
            'get_serial': self._get_serial_number,
            'get_action': self.get_type_action,
            'get_action_date': self.get_action_date,
        })

    def _get_priority(self, priority):
        if priority:
            for k,v in AVAILABLE_PRIORITIES:
                if k == priority:
                    return _(v)
        return ""

    def _get_serial_number(self, claim):
        if not hasattr(claim, 'ref'):
            return False
        if claim.ref:
            if str(claim.ref._model) == 'stock.production.lot':
                return claim.ref.name
        return False

    def get_type_action(self, action):
        if action:
            for k,v in AVAILABLE_ACTIONS:
                if k == action:
                    return _(v)
        return ""

    def get_action_date(self, claim):
        if claim.date_closed:
            return claim.date_closed
        return claim.write_date

report_sxw.report_sxw('report.crm.claim',
                      'crm.claim',
                      'addons/crm_claim_report/report/crm_claim.rml',parser=crm_claim)
