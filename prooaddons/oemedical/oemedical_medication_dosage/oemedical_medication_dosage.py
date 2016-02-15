from openerp import models,fields


class OeMedicalMedicationDosage(models.Model):
    _name = 'oemedical.medication.dosage'

    abbreviation = fields.Char(size=256, string='Abbreviation',
        help='Dosage abbreviation, such as tid in the US or tds in the UK')
    code = fields.Char(size=8, string='Code',
        help='Dosage Code,for example: SNOMED 229798009 = 3 times per day')
    name = fields.Char(size=256, string='Frequency', required=True,
                        translate=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
