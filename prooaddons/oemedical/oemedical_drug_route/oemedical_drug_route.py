from openerp import models,fields


class OeMedicalDrugRoute(models.Model):
    _name = 'oemedical.drug.route'

    code = fields.Char(size=256, string='Code')
    name = fields.Char(size=256, string='Unit', required=True,
                        translate=True)
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
