from openerp import models,fields


class OeMedicalDrugForm(models.Model):
    _name = 'oemedical.drug.form'


    code = fields.Char(size=256, string='Code')
    name = fields.Char(size=256, string='Form', required=True,
                        translate=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
