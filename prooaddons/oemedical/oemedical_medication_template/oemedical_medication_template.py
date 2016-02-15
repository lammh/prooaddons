from openerp import models,fields


class OeMedicalMedicationTemplate(models.Model):
    _name = 'oemedical.medication.template'

    def _get_name(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.medicament_id.name
        return res



    medicament_id = fields.Many2one('oemedical.medicament', string='Medicament', requered=True, help='Product Name', ondelete='cascade')
    name = fields.Char(compute ='_get_name', string='Medicament', help="", multi=False)
    indication = fields.Many2one('oemedical.pathology', string='Indication', help='Choose a disease for this medicament from the disease list. It'\
                    ' can be an existing disease of the patient or a prophylactic.')
    start_treatment = fields.Datetime(string='Start', help='Date of start of Treatment')
    end_treatment = fields.Datetime(string='End', help='Date of start of Treatment')
    form = fields.Many2one('oemedical.drug.form', string='Form', help='Drug form, such as tablet or gel')
    route = fields.Many2one('oemedical.drug.route', string='Administration Route', help='Drug administration route code.')
    duration_period = fields.Selection([
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('months', 'months'),
        ('years', 'years'),
        ('indefinite', 'indefinite'),
    ], string='Treatment period', help='Period that the patient must take the medication in minutes, hours, days, months, years or indefinately')
    qty = fields.Integer(string='x', help='Quantity of units (eg, 2 capsules) of the medicament')
    frequency_unit = fields.Selection([
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('wr', 'when required'),
    ], string='unit')
    dose = fields.Float(string='Dose', help='Amount of medication (eg, 250 mg) per dose')
    duration = fields.Integer(string='Treatment duration', help='Period that the patient must take the medication. in minutes,'\
    ' hours, days, months, years or indefinately')
    frequency_prn = fields.Boolean(string='PRN',  help='Use it as needed, pro re nata')
    frequency = fields.Integer(string='Frequency',  help='Time in between doses the patient must wait (ie, for 1 pill'\
        ' each 8 hours, put here 8 and select \"hours\" in the unit field')
    common_dosage = fields.Many2one('oemedical.medication.dosage', string='Frequency', help='Common / standard dosage frequency for this medicament')
    admin_times = fields.Char(size=256, string='Admin hours', help='Suggested administration hours. For example, at 08:00, 13:00 and 18:00 can be encoded like 08 13 18')
    dose_unit = fields.Many2one('product.uom', string='dose unit', help='Unit of measure for the medication to be taken')
