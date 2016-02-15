from openerp import models,fields


class OeMedicalHospitalBed(models.Model):
    _name = 'oemedical.hospital.bed'

    name = fields.Many2one('product.product', string='Bed',required=True,
                            help='Bed Number')
    bed_type = fields.Selection([
        ('gatch', 'Gatch Bed'),
        ('electric', 'Electric'),
        ('stretcher', 'Stretcher'),
        ('low', 'Low Bed'),
        ('low_air_loss', 'Low Air Loss'),
        ('circo_electric', 'Circo Electric'),
        ('clinitron', 'Clinitron'),
    ], string='Bed Type',required=True)
    telephone_number = fields.Char(size=256, string='Telephone Number',
                                    help='Telephone number / Extension')
    state = fields.Selection([
        ('free', 'Free'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
        ('na', 'Not available'),
    ], string='Status',readonly=True)
    ward = fields.Many2one('oemedical.hospital.ward', string='Ward',
                             help='Ward or room')
    extra_info = fields.Text(string='Extra Info')
