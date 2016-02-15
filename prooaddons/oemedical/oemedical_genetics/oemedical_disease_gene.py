from openerp import models,fields


class OeMedicalDiseaseGene(models.Model):

    _name = 'oemedical.disease.gene'
    _description = 'Disease Genes'


    name = fields.Char('Official Symbol', size=256, required=True)
    gene_id = fields.Char('Gene ID', size=256)
    long_name = fields.Char('Official Long Name', size=256, required=True)
    location = fields.Char('Location', size=256, required=True, help="Locus of the chromosome")
    chromosome = fields.Char('Affected Chromosome', size=256, required=True)
    info = fields.Text(string='Information')
    dominance = fields.Selection([
                ('d', 'dominant'),
                ('r', 'recessive'),
                ], 'Dominance', select=True)



class PatientGeneticRisk(models.Model):
    
    _name = 'oemedical.patient.genetic.risk'
    _description = 'Patient Genetic Risks'

    patient_id = fields.Many2one('oemedical.patient', 'Patient', select=True)
    disease_gene = fields.Many2one('oemedical.disease.gene', 'Disease Gene', required=True)


class FamilyDiseases(models.Model):
    
    _name = 'oemedical.patient.family.diseases'
    _description = 'Family Diseases'

    patient_id = fields.Many2one('oemedical.patient', 'Patient', select=True)
    name = fields.Many2one('oemedical.pathology', 'Disease', required=True)
    xory = fields.Selection([
            ('m', 'Maternal'),
            ('f', 'Paternal'),
            ], 'Maternal or Paternal', select=True)
    relative = fields.Selection([
            ('mother', 'Mother'),
            ('father', 'Father'),
            ('brother', 'Brother'),
            ('sister', 'Sister'),
            ('aunt', 'Aunt'),
            ('uncle', 'Uncle'),
            ('nephew', 'Nephew'),
            ('niece', 'Niece'),
            ('grandfather', 'Grandfather'),
            ('grandmother', 'Grandmother'),
            ('cousin', 'Cousin'),
            ], 'Relative',
            help="First degree = siblings, mother and father; second degree = "
            "Uncles, nephews and Nieces; third degree = Grandparents and cousins",
            required=True)

class oemedicalPatient(models.Model):
    'Add to the Medical patient_data class (oemedical.patient) the genetic ' \
    'and family risks'
    _inherit='oemedical.patient'

    genetic_risks = fields.One2many('oemedical.patient.genetic.risk', 'patient_id', 'Genetic Risks')
    family_history = fields.One2many('oemedical.patient.family.diseases', 'patient_id', 'Family History')
