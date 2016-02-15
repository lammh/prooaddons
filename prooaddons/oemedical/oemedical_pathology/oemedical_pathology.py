from openerp import models,fields


class OeMedicalPathology(models.Model):
    _name = 'oemedical.pathology'


    category = fields.Many2one('oemedical.pathology.category', string='Main Category',
          help='Select the main category for this disease This is usually'\
    'associated to the standard. For instance, the chapter on the ICD-10'\
    'will be the main category for de disease' )
    info = fields.Text(string='Extra Info')
    code = fields.Char(size=256, string='Code', required=True, help='Specific Code for the Disease (eg, ICD-10)')
    name = fields.Char(size=256, string='Name', required=True, translate=True, help='Disease name')
    groups = fields.One2many('oemedical.disease_group.members', 'disease_group_id', string='Groups',
                 help='Specify the groups this pathology belongs. Some' \
                 ' automated processes act upon the code of the group' )
    protein = fields.Char(size=256, string='Protein involved', help='Name of the protein(s) affected')
    gene = fields.Char(size=256, string='Gene')
    chromosome = fields.Char(size=256, string='Affected Chromosome', help='chromosome number')

