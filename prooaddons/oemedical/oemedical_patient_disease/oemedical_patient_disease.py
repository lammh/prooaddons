from openerp import models,fields


class OeMedicalPatientDisease(models.Model):
    _name = 'oemedical.patient.disease'

    treatment_description = fields.Char(size=256,
                                         string='Treatment Description')
    healed_date = fields.Date(string='Healed')
    pathology = fields.Many2one('oemedical.pathology',
                                 string='Disease',help='Disease')
    disease_severity = fields.Selection([
        ('1_mi', 'Mild'),
        ('2_mo', 'Moderate'),
        ('3_sv', 'Severe'),
    ], string='Severity',select=True, sort=False)
    is_allergy = fields.Boolean(string='Allergic Disease')
    doctor = fields.Many2one('oemedical.physician', string='Physician',
                    help='Physician who treated or diagnosed the patient')
    pregnancy_warning = fields.Boolean(string='Pregnancy warning')
    weeks_of_pregnancy = fields.Integer(
        string='Contracted in pregnancy week #')
    is_on_treatment = fields.Boolean(string='Currently on Treatment')
    diagnosed_date = fields.Date(string='Date of Diagnosis')
    extra_info = fields.Text(string='Extra Info')
    status = fields.Selection([
        ('a', 'acute'),
        ('c', 'chronic'),
        ('u', 'unchanged'),
        ('h', 'healed'),
        ('i', 'improving'),
        ('w', 'worsening'),
    ], string='Status of the disease',select=True, sort=False)
    is_active = fields.Boolean(string='Active disease')
    date_stop_treatment = fields.Date(string='End',
                                       help='End of treatment date')
    pcs_code = fields.Many2one('oemedical.procedure', string='Code',
    help='Procedure code, for example, ICD-10-PCS Code 7-character string')
    is_infectious = fields.Boolean(string='Infectious Disease',
                            help='Check if the patient has an infectious' \
                            'transmissible disease')
    allergy_type = fields.Selection([
        ('da', 'Drug Allergy'),
        ('fa', 'Food Allergy'),
        ('ma', 'Misc Allergy'),
        ('mc', 'Misc Contraindication'),
    ], string='Allergy type',select=True, sort=False)
    patient_id = fields.Many2one('oemedical.patient', string='Patient', )
    age = fields.Integer(string='Age when diagnosed',
      help='Patient age at the moment of the diagnosis. Can be estimative')
    date_start_treatment = fields.Date(string='Start',
                                        help='Start of treatment date')
    short_comment = fields.Char(size=256, string='Remarks',
    help='Brief, one-line remark of the disease. Longer description will'\
    ' go on the Extra info field')
