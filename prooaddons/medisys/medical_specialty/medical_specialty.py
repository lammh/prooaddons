from openerp import models,fields


class MedicalSpecialty(models.Model):
    _name = 'medical.specialty'

    name = fields.Char(size=256, string='Specialty', required=True, translate=True)
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
