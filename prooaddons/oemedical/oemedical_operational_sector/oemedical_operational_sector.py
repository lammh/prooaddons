from openerp import models,fields


class OeMedicalOperationalSector(models.Model):
    _name = 'oemedical.operational_sector'

    info = fields.Text(string='Extra Information')
    operational_area_id = fields.Many2one('oemedical.operational_area',
                                           string='Operational Area', )
    name = fields.Char(size=256, string='Op. Sector', required=True,
                        help='Region included in an operational area')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
