from openerp import models,fields


class OeMedicalSpecialty(models.Model):
    _name = 'oemedical.specialty'

    code = fields.Char(string='Code')
    name = fields.Char(size=256, string='Specialty', required=True,
                        translate=True)
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
