from openerp import models,fields


class OeMedicalDiseaseGroupMembers(models.Model):
    _name = 'oemedical.disease_group.members'

    disease_group_id = fields.Many2one('oemedical.pathology.group',
                                        string='Group',required=True )
    name = fields.Many2one('oemedical.pathology', string='Disease',
                                readonly=True )
