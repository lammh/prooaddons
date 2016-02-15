from openerp import models,fields

class OeMedicalHospitalOr(models.Model):
    _name = 'oemedical.hospital.or'

    building = fields.Many2one('oemedical.hospital.building', 'Building',
                                select=True)
    name = fields.Char(size=256, string='Name', required=True,
                        help='Name of the Operating Room')
    institution = fields.Many2one('res.partner', string='Institution',
                                   help='Medical Center')
    unit = fields.Many2one('oemedical.hospital.unit', string='Unit', )
    extra_info = fields.Text(string='Extra Info')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
