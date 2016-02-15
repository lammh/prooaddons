from openerp import models,fields,api


class MedicalRoom(models.Model):
    _name = 'medical.room'

    name = fields.Char(size=256, string='Name', required=True)
    categ_id = fields.Many2one('product.product', 'Category', domain="[('is_categ_room', '=', True)]", required=True)
    state = fields.Selection([
                               ('free', 'Free'),
                               ('ready', 'Ready'),
                               ('occupied', 'Occupied'),
                               ('repair', 'Repair'),
                               ('reserved', 'Reserved'), ], string='State')

    _defaults={
            'state': 'free',
                 }
