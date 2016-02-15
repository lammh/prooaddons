# -*- coding: utf-8 -*-

from openerp import models, fields, api


class product_template(models.Model):
    _inherit = 'product.template'

    pharmacy = fields.Boolean(string='Pharmacy')
    stewardship = fields.Boolean(string='Stewardship')

class product_category(models.Model):
    _inherit = 'product.category'

    pharmacy = fields.Boolean(string='Pharmacy')
    stewardship = fields.Boolean(string='Stewardship')

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    pharmacy = fields.Boolean(string='Pharmacy')
    stewardship = fields.Boolean(string='Stewardship')

class res_partner(models.Model):
    _inherit = 'res.partner'

    pharmacy = fields.Boolean(string='Pharmacy')
    stewardship = fields.Boolean(string='Stewardship')