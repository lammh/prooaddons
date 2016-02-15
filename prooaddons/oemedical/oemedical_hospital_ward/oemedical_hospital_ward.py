from openerp import models,fields


class OeMedicalHospitalWard(models.Model):
    _name = 'oemedical.hospital.ward'


    building = fields.Many2one('oemedical.hospital.building',
                                string='Building', )
    ac = fields.Boolean(string='Air Conditioning')
    name = fields.Char(size=256, string='Name', required=True,
                        help='Ward / Room code')
    floor = fields.Integer(string='Floor Number')
    tv = fields.Boolean(string='Television')
    gender = fields.Selection([('men', 'Men Ward'),
                                ('women', 'Women Ward'),
                                ('unisex', 'Unisex')],
                               string='Gender',required=True)
    unit = fields.Many2one('oemedical.hospital.unit', string='Unit', )
    private_bathroom = fields.Boolean(string='Private Bathroom')
    telephone = fields.Boolean(string='Telephone access')
    microwave = fields.Boolean(string='Microwave')
    guest_sofa = fields.Boolean(string='Guest sofa-bed')
    state = fields.Selection([
        ('beds_available', 'Beds available'),
        ('full', 'Full'),
        ('na', 'Not available'),
    ], string='Status')
    private = fields.Boolean(string='Private',
                              help='Check this option for private room')
    number_of_beds = fields.Integer(string='Number of beds',
                                     help='Number of patients per ward')
    internet = fields.Boolean(string='Internet Access')
    bio_hazard = fields.Boolean(string='Bio Hazard',
                    help='Check this option if there is biological hazard')
    institution = fields.Many2one('res.partner', string='Institution',
                                   help='Medical Center')
    refrigerator = fields.Boolean(string='Refrigetator')
    extra_info = fields.Text(string='Extra Info')
