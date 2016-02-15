from openerp import models,fields


class Product(models.Model):
    _inherit = 'product.template'

    is_categ_room = fields.Boolean(string='Room Category', help='Check if the product is a room category')


