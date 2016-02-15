# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class pos_order_line(models.Model):
    _inherit = 'account.period'

    apply_price_list = fields.Boolean('Apply price list', default=True)
