# -*- coding: utf-8 -*-
from openerp import models, fields

class res_partner(models.Model):
    _inherit = 'res.partner'

    warranty = fields.One2many('account.treasury', 'partner_id', string='Warranty', domain=[('state', '=', 'warranty')])

