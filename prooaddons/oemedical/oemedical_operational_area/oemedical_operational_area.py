from openerp import models,fields


class OeMedicalOperationalArea(models.Model):
    _name = 'oemedical.operational_area'


    info = fields.Text(string='Extra Information')
    operational_sector = fields.One2many('oemedical.operational_sector',
                                          'operational_area_id',
                                          string='Operational Sector',
                                          readonly=True)
    name = fields.Char(size=256, string='Name', required=True,
                        help='Operational Area of the city or region')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
