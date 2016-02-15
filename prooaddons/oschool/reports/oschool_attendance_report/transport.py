# -*- coding: utf-8 -*-
from openerp import fields, models, api, exceptions

import logging
_logger = logging.getLogger(__name__)

class transport_wizard(models.Model):
    _name = 'oschool.transport.wizard'

    zone_id = fields.Many2one('oschool.zone', string="Zone")
    period_id = fields.Many2one('account.period', 'Period')
    presence_ids = fields.One2many('oschool.student_transport_presence','report_id')

    def create(self, cr, uid, vals):
        presence_obj = self.pool.get('oschool.student_transport_presence')
        presence_ids = presence_obj.search(cr, uid, [
            ('zone_id', '=', vals['zone_id']),
            ('period_id', '=', vals['period_id']),
            ('dayNum', '=', 1),
        ])
        r = []
        for id in presence_ids:
            r.append([4,id])
        vals['presence_ids'] = r

        return  super(transport_wizard, self).create(cr, uid, vals)
