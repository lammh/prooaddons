from openerp import models,fields


class OeMedicalPatientMedication(models.Model):
    _name = 'oemedical.patient.medication'

    patient_id = fields.Many2one('oemedical.patient', string='Patient',)
#        'name': fields.many2one('oemedical.patient', string='Patient',
#                                readonly=True ),
    doctor = fields.Many2one('oemedical.physician', string='Physician',
                            help='Physician who prescribed the medicament')
    adverse_reaction = fields.Text(string='Adverse Reactions',
    help='Side effects or adverse reactions that the patient experienced')
    notes = fields.Text(string='Extra Info')
    is_active = fields.Boolean(string='Active',
            help='Check if the patient is currently taking the medication')
    course_completed = fields.Boolean(string='Course Completed')
    template = fields.Many2one('oemedical.medication.template',
                                string='Medication Template', )
    discontinued_reason = fields.Char(size=256,
                                       string='Reason for discontinuation',
                help='Short description for discontinuing the treatment')
    discontinued = fields.Boolean(string='Discontinued')
