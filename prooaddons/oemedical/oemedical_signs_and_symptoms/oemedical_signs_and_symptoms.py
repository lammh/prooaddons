from openerp import models,fields


class OeMedicalSignsAndSymptoms(models.Model):
    _name = 'oemedical.signs_and_symptoms'

    clinical_id = fields.Many2one('oemedical.pathology',
                                   'Sign or Symptom',required=True )
    evaluation_id = fields.Many2one('oemedical.patient.evaluation',
                                     string='Evaluation',readonly=True)
    sign_or_symptom = fields.Selection([
        ('sign', 'Sign'),
        ('symptom', 'Symptom'),
    ], string='Subjective / Objective',required=True)
    comments = fields.Char(size=256, string='Comments')


