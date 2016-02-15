from openerp import models,fields
#from dateutil.relativedelta import relativedelta
#from datetime import datetime


class OeMedicalSocioeconomics(models.Model):

    _inherit='oemedical.patient'


    ses = fields.Selection([
        (None, ''),
        ('0', 'Lower'),
        ('1', 'Lower-middle'),
        ('2', 'Middle'),
        ('3', 'Middle-upper'),
        ('4', 'Higher'),
        ], 'Socioeconomics', help="SES - Socioeconomic Status", sort=False)
    housing = fields.Selection([
        (None, ''),
        ('0', 'Shanty, deficient sanitary conditions'),
        ('1', 'Small, crowded but with good sanitary conditions'),
        ('2', 'Comfortable and good sanitary conditions'),
        ('3', 'Roomy and excellent sanitary conditions'),
        ('4', 'Luxury and excellent sanitary conditions'),
        ], 'Housing conditions', help="Housing and sanitary living conditions", sort=False)
    hostile_area = fields.Boolean('Hostile Area', help="Check if patient lives in a zone of high hostility (eg, war)")
    sewers = fields.Boolean('Sanitary Sewers')
    water = fields.Boolean('Running Water')
    trash = fields.Boolean('Trash recollection')
    electricity = fields.Boolean('Electrical supply')
    gas = fields.Boolean('Gas supply')
    telephone = fields.Boolean('Telephone')
    television = fields.Boolean('Television')
    internet = fields.Boolean('Internet')
    single_parent = fields.Boolean('Single parent family')
    domestic_violence = fields.Boolean('Domestic violence')
    working_children = fields.Boolean('Working children')
    teenage_pregnancy = fields.Boolean('Teenage pregnancy')
    sexual_abuse = fields.Boolean('Sexual abuse')
    drug_addiction = fields.Boolean('Drug addiction')
    school_withdrawal = fields.Boolean('School withdrawal')
    prison_past = fields.Boolean('Has been in prison')
    prison_current = fields.Boolean('Is currently in prison')
    relative_in_prison = fields.Boolean('Relative in prison', help="Check if someone from the nuclear family - parents sibblings  is or has been in prison")
    ses_notes = fields.Text('Extra info')
    fam_apgar_help = fields.Selection([
        (None, ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
        ], 'Help from family',
        help="Is the patient satisfied with the level of help coming from the family when there is a problem ?", sort=False)
    fam_apgar_discussion = fields.Selection([
        (None, ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
        ], 'Problems discussion',
        help="Is the patient satisfied with the level talking over the problems as family ?", sort=False)
    fam_apgar_decisions = fields.Selection([
        (None, ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
        ], 'Decision making',
        help="Is the patient satisfied with the level of making important decisions as a group ?", sort=False)
    fam_apgar_timesharing = fields.Selection([
        (None, ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
        ], 'Time sharing',
        help="Is the patient satisfied with the level of time that they spend together ?", sort=False)
    fam_apgar_affection = fields.Selection([
        (None, ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
        ], 'Family affection',
        help="Is the patient satisfied with the level of affection coming from the family ?", sort=False)
    fam_apgar_score = fields.Integer('Score', help="Total Family APGAR 7 - 10 : Functional Family 4 - 6  : Some level of disfunction \n" \
        "0 - 3  : Severe disfunctional family \n")
    income = fields.Selection([
        (None, ''),
        ('h', 'High'),
        ('m', 'Medium / Average'),
        ('l', 'Low'),
        ], 'Income', sort=False)
    education = fields.Selection([
        (None, ''),
        ('0', 'None'),
        ('1', 'Incomplete Primary School'),
        ('2', 'Primary School'),
        ('3', 'Incomplete Secondary School'),
        ('4', 'Secondary School'),
        ('5', 'University'),
        ], 'Education Level', help="Education Level", sort=False)
    works_at_home = fields.Boolean('Works at home', help="Check if the patient works at his / her house")
    hours_outside = fields.Integer('Hours outside home', help="Number of hours a day the patient spend outside the house")
