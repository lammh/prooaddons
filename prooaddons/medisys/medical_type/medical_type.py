from openerp import models,fields,api


class MedicalType(models.Model):
    _name = 'medical.type'

    name = fields.Char(size=256, string='Type')
