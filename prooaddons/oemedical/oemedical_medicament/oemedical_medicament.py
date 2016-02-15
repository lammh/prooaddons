from openerp import models,fields,api


class OeMedicalMedicament(models.Model):
    _name = 'oemedical.medicament'

    @api.one
    @api.depends('product_id')
    def _get_name(self):
        self.name = self.product_id

    product_id = fields.Many2one('product.product', string='Medicament', requered=True, help='Product Name')
    name = fields.Char(compute = '_get_name', string='Medicament', help="", multi=False)
    category = fields.Many2one('oemedical.medicament.category', 'Category',select=True)
    active_component = fields.Char(size=256, string='Active component', help='Active Component')
    indications = fields.Text(string='Indication', help='Indications')
    therapeutic_action = fields.Char(size=256, string='Therapeutic effect', help='Therapeutic action')
    pregnancy_category = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('X', 'X'),
        ('N', 'N'),
        ], string='Pregnancy Category',
        help='** FDA Pregancy Categories ***\n'\
    'CATEGORY A :Adequate and well-controlled human studies have failed'\
    ' to demonstrate a risk to the fetus in the first trimester of'\
    ' pregnancy (and there is no evidence of risk in later'\
    ' trimesters).\n\n'\
    'CATEGORY B : Animal reproduction studies have failed todemonstrate a'\
    ' risk to the fetus and there are no adequate and well-controlled'\
    ' studies in pregnant women OR Animal studies have shown an adverse'\
    ' effect, but adequate and well-controlled studies in pregnant women'\
    ' have failed to demonstrate a risk to the fetus in any'\
    ' trimester.\n\n'
    'CATEGORY C : Animal reproduction studies have shown an adverse'\
    ' effect on the fetus and there are no adequate and well-controlled'\
    ' studies in humans, but potential benefits may warrant use of the'\
    ' drug in pregnant women despite potential risks. \n\n '\
    'CATEGORY D : There is positive evidence of human fetal  risk based'\
    ' on adverse reaction data from investigational or marketing'\
    ' experience or studies in humans, but potential benefits may warrant'\
    ' use of the drug in pregnant women despite potential risks.\n\n'\
    'CATEGORY X : Studies in animals or humans have demonstrated fetal'\
    ' abnormalities and/or there is positive evidence of human fetal risk'\
    ' based on adverse reaction data from investigational or marketing'\
    ' experience, and the risks involved in use of the drug in pregnant'\
    ' women clearly outweigh potential benefits.\n\n'\
    'CATEGORY N : Not yet classified')

    overdosage = fields.Text(string='Overdosage', help='Overdosage')
    pregnancy_warning = fields.Boolean(string='Pregnancy Warning',
                help='The drug represents risk to pregnancy or lactancy')
    notes = fields.Text(string='Extra Info')
    storage = fields.Text(string='Storage Conditions')
    adverse_reaction = fields.Text(string='Adverse Reactions')
    dosage= fields.Text(string='Dosage Instructions',
                          help='Dosage / Indications')
    pregnancy = fields.Text(string='Pregnancy and Lactancy',
                             help='Warnings for Pregnant Women')
    presentation = fields.Text(string='Presentation')
    composition = fields.Text(string='Composition', help='Components')
