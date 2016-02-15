from openerp import models,fields


class OeMedicalOccupation(models.Model):
    _name = 'oemedical.occupation'

    code = fields.Char(size=256, string='Code')
    name = fields.Char(size=256, string='Name', required=True ,
                        translate=True)
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]