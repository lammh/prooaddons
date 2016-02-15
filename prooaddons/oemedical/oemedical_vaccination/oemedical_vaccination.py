from openerp import models,fields


class OeMedicalVaccination(models.Model):
    _name = 'oemedical.vaccination'


    name = fields.Char(size=256, string='Name')
    vaccine_lot = fields.Char(size=256, string='Lot Number',
    help='Please check on the vaccine (product) production lot numberand'\
    ' tracking number when available !')
    patient_id = fields.Many2one('oemedical.patient', string='Patient',
                                  readonly=True )
    vaccine = fields.Many2one('product.product', string='Vaccine',
                               required=True,
    help='Vaccine Name. Make sure that the vaccine (product) has all the'\
    ' proper information at product level. Information such as provider,'\
    ' supplier code, tracking number, etc.. This  information must always'\
    ' be present. If available, please copy / scan the vaccine leaflet'\
    ' and attach it to this record')
    dose = fields.Integer(string='Dose #')
    observations = fields.Char(size=256, string='Observations',
                                required=True)
    date = fields.Datetime(string='Date')
    institution = fields.Many2one('res.partner', string='Institution',
        help='Medical Center where the patient is being or was vaccinated')
    next_dose_date = fields.Datetime(string='Next Dose')
