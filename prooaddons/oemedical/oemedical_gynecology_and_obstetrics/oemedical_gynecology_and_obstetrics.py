from openerp import models,fields

class PatientPregnancy(models.Model):
    
    _name = 'oemedical.patient.pregnancy'
    _description = 'Patient Pregnancy'

    def _get_pregnancy_data(self, cr, uid, ids, name, args, context=None):
#        if name == 'pdd':
#            return self.lmp + datetime.timedelta(days=280)
#        if name == 'pregnancy_end_age':
#            if self.pregnancy_end_date:
#                gestational_age = datetime.datetime.date(
#                    self.pregnancy_end_date) - self.lmp
#                return (gestational_age.days) / 7
#            else:
        return 2

    name = fields.Many2one('oemedical.patient', 'Patient ID')
    gravida = fields.Integer('Pregnancy ', required=True)
    warning = fields.Boolean('Warn', help='Check this box if this is pregancy is or was NOT normal')
    lmp = fields.Date('LMP', help="Last Menstrual Period", required=True)
    pdd = fields.Date(compute= '_get_pregnancy_data', string='Pregnancy Due Date')
    prenatal_evaluations = fields.One2many('oemedical.patient.prenatal.evaluation', 'name', 'Prenatal Evaluations')
    perinatal = fields.One2many('oemedical.perinatal', 'name', 'Perinatal Info')
    puerperium_monitor = fields.One2many('oemedical.puerperium.monitor', 'name', 'Puerperium monitor')
    current_pregnancy = fields.Boolean('Current Pregnancy', help='This field marks the current pregnancy')
    fetuses = fields.Integer('Fetuses', required=True)
    monozygotic = fields.Boolean('Monozygotic')
    pregnancy_end_result = fields.Selection([
                    ('live_birth', 'Live birth'),
                    ('abortion', 'Abortion'),
                    ('stillbirth', 'Stillbirth'),
                    ('status_unknown', 'Status unknown'),
                    ], 'Result', sort=False,)
    pregnancy_end_date = fields.Datetime('End of Pregnancy',)
    pregnancy_end_age = fields.Char(compute = '_get_pregnancy_data', string='Weeks', help='Weeks at the end of pregnancy')
    iugr = fields.Selection([
                    ('symmetric', 'Symmetric'),
                    ('assymetric', 'Assymetric'),
                    ], 'IUGR', sort=False)


class PrenatalEvaluation(models.Model):

    _name = 'oemedical.patient.prenatal.evaluation'
    _description =  'Prenatal and Antenatal Evaluations'

    def _get_patient_evaluation_data(self, cr, uid, ids, field_name, args, context=None):
        #result = dict([(i, {}.fromkeys(field_names, 0.0)) for i in ids])
        #print result
#        print ids, field_name, arg
#        if name == 'gestational_weeks':
#            gestational_age = datetime.datetime.date(self.evaluation_date) - \
#                self.name.lmp
#            return (gestational_age.days) / 7
#        if name == 'gestational_days':
#            gestational_age = datetime.datetime.date(self.evaluation_date) - \
#                self.name.lmp
#            return gestational_age.days
        return 20



    name = fields.Many2one('oemedical.patient.pregnancy', 'Patient Pregnancy')
    evaluation = fields.Many2one('oemedical.patient.evaluation', 'Patient Evaluation', readonly=True)
    evaluation_date = fields.Datetime('Date', required=True)
    gestational_weeks = fields.Float(compute = '_get_patient_evaluation_data', method=True , string="Gestational Weeks")
    gestational_days = fields.Integer(compute = '_get_patient_evaluation_data', method=True , string='Gestational days' )
    hypertension = fields.Boolean('Hypertension', help='Check this box if the mother has hypertension')
    preeclampsia = fields.Boolean('Preeclampsia', help='Check this box if the mother has pre-eclampsia')
    overweight = fields.Boolean('Overweight', help='Check this box if the mother is overweight or obesity')
    diabetes = fields.Boolean('Diabetes', help='Check this box if the mother has glucose intolerance or diabetes')
    invasive_placentation = fields.Selection([
                ('normal', 'Normal decidua'),
                ('accreta', 'Accreta'),
                ('increta', 'Increta'),
                ('percreta', 'Percreta'),
                ], 'Placentation')
    placenta_previa = fields.Boolean('Placenta Previa')
    vasa_previa = fields.Boolean('Vasa Previa')
    fundal_height = fields.Integer('Fundal Height', help="Distance between the symphysis pubis and the uterine fundus (S-FD) in cm")
    fetus_heart_rate = fields.Integer('Fetus heart rate', help='Fetus heart rate')
    efw = fields.Integer('EFW', help="Estimated Fetal Weight")
    fetal_bpd = fields.Integer('BPD', help="Fetal Biparietal Diameter")
    fetal_ac = fields.Integer('AC', help="Fetal Abdominal Circumference")
    fetal_hc = fields.Integer('HC', help="Fetal Head Circumference")
    fetal_fl = fields.Integer('FL', help="Fetal Femur Length")
    oligohydramnios = fields.Boolean('Oligohydramnios')
    polihydramnios = fields.Boolean('Polihydramnios')
    iugr = fields.Boolean('IUGR', help="Intra Uterine Growth Restriction")



class PuerperiumMonitor(models.Model):

    _name = 'oemedical.puerperium.monitor'
    _description = 'Puerperium Monitor'

    name = fields.Many2one('oemedical.patient', string='Patient ID')
    date = fields.Datetime('Date and Time', required=True)
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    frequency = fields.Integer('Heart Frequency')
    lochia_amount = fields.Selection([
        ('n', 'normal'),
        ('e', 'abundant'),
        ('h', 'hemorrhage'),
        ], 'Lochia amount', select=True)
    lochia_color = fields.Selection([
        ('r', 'rubra'),
        ('s', 'serosa'),
        ('a', 'alba'),
        ], 'Lochia color', select=True)
    lochia_odor = fields.Selection([
        ('n', 'normal'),
        ('o', 'offensive'),
        ], 'Lochia odor', select=True)
    uterus_involution = fields.Integer('Fundal Height', help="Distance between the symphysis pubis and the uterine fundus (S-FD) in cm")
    temperature = fields.Float('Temperature')


class PerinatalMonitor(models.Model):
    
    _name = 'oemedical.perinatal.monitor'
    _description = 'Perinatal monitor'

    name = fields.Many2one('oemedical.patient', string='patient_id')
    date = fields.Datetime('Date and Time')
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    contractions = fields.Integer('Contractions')
    frequency = fields.Integer('Mother\'s Heart Frequency')
    dilation = fields.Integer('Cervix dilation')
    f_frequency = fields.Integer('Fetus Heart Frequency')
    meconium = fields.Boolean('Meconium')
    bleeding = fields.Boolean('Bleeding')
    fundal_height = fields.Integer('Fundal Height')
    fetus_position = fields.Selection([
        ('n', 'Correct'),
        ('o', 'Occiput / Cephalic Posterior'),
        ('fb', 'Frank Breech'),
        ('cb', 'Complete Breech'),
        ('t', 'Transverse Lie'),
        ('t', 'Footling Breech'),
        ], 'Fetus Position', select=True)

class OemedicalPerinatal(models.Model):

    _name = 'oemedical.perinatal'
    _description =  'Perinatal Information'

    name = fields.Many2one('oemedical.patient', string='Perinatal Infomation')
    admission_code = fields.Char('Admission Code', size=64)
    gravida_number = fields.Integer('Gravida #')
    abortion = fields.Boolean('Abortion')
    admission_date = fields.Datetime('Admission date', help="Date when she was admitted to give birth")
    prenatal_evaluations = fields.Integer('Prenatal evaluations', help="Number of visits to the doctor during pregnancy")
    start_labor_mode = fields.Selection([
        ('n', 'Normal'),
        ('i', 'Induced'),
        ('c', 'c-section'),
        ], 'Labor mode', select=True)
    gestational_weeks = fields.Integer('Gestational weeks')
    gestational_days = fields.Integer('Gestational days')
    fetus_presentation = fields.Selection([
                    ('n', 'Correct'),
                    ('o', 'Occiput / Cephalic Posterior'),
                    ('fb', 'Frank Breech'),
                    ('cb', 'Complete Breech'),
                    ('t', 'Transverse Lie'),
                    ('t', 'Footling Breech'),
                    ], 'Fetus Presentation', select=True)
    dystocia = fields.Boolean('Dystocia')
    laceration = fields.Selection([
                    ('perineal', 'Perineal'),
                    ('vaginal', 'Vaginal'),
                    ('cervical', 'Cervical'),
                    ('broad_ligament', 'Broad Ligament'),
                    ('vulvar', 'Vulvar'),
                    ('rectal', 'Rectal'),
                    ('bladder', 'Bladder'),
                    ('urethral', 'Urethral'),
                    ], 'Lacerations', sort=False)
    hematoma = fields.Selection([
                    ('vaginal', 'Vaginal'),
                    ('vulvar', 'Vulvar'),
                    ('retroperitoneal', 'Retroperitoneal'),
                    ], 'Hematoma', sort=False)
    placenta_incomplete = fields.Boolean('Incomplete Placenta')
    placenta_retained = fields.Boolean('Retained Placenta')
    abruptio_placentae = fields.Boolean('Abruptio Placentae', help='Abruptio Placentae')
    episiotomy = fields.Boolean('Episiotomy')
    vaginal_tearing = fields.Boolean('Vaginal tearing')
    forceps = fields.Boolean('Use of forceps')
    monitoring = fields.One2many('oemedical.perinatal.monitor', 'name', string='Monitors')
    puerperium_monitor = fields.One2many('oemedical.puerperium.monitor', 'name','Puerperium monitor')
    medications = fields.One2many('oemedical.patient.medication','patient_id', string='Medications',)
    dismissed = fields.Datetime('Dismissed from hospital')
    place_of_death = fields.Selection([
        ('ho', 'Hospital'),
        ('dr', 'At the delivery room'),
        ('hh', 'in transit to the hospital'),
        ('th', 'Being transferred to other hospital'),
        ], 'Place of Death')
    mother_deceased = fields.Boolean('Deceased', help="Mother died in the process")
    notes = fields.Text('Notes')


class OeMedicalPatient(models.Model):

    _inherit='oemedical.patient'

    def _get_pregnancy_info(self, cr, uid, ids, name, args, context=None):
#        if name == 'currently_pregnant':
#            for pregnancy_history in self.pregnancy_history:
#                if pregnancy_history.current_pregnancy:
#                    return True
        return False


    currently_pregnant = fields.Boolean('Currently Pregnant')
#            'currently_pregnant' : fields.function( _get_pregnancy_info , string='Pregnant' , type='boolean' ),
    fertile = fields.Boolean('Fertile', help="Check if patient is in fertile age")
    dispareunia_sup = fields.Boolean('Dyspareunia Superficial', help="")
    dispareunia_deep = fields.Boolean('Dyspareunia Deep', help="")
    menarche = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    menopause = fields.Integer('Menopause age')
    mammography = fields.Boolean('Mammography', help="Check if the patient does periodic mammographys")
    mammography_last = fields.Date('Last mammography', help="Enter the date of the last mammography")
    breast_self_examination = fields.Boolean('Breast self-examination', help="Check if patient does and knows how to self examine her breasts")
    pap_test = fields.Boolean('PAP test',  help="Check if patient does periodic cytologic pelvic smear screening")
    pap_test_last = fields.Date('Last PAP test', help="Enter the date of the last Papanicolau test")
    colposcopy = fields.Boolean('Colposcopy', help="Check if the patient has done a colposcopy exam")
    colposcopy_last = fields.Date('Last colposcopy', help="Enter the date of the last colposcopy")
    gravida = fields.Integer('Gravida', help="Number of pregnancies")
    premature = fields.Integer('Premature', help="Premature Deliveries")
    abortions = fields.Integer('Abortions')
    stillbirths = fields.Integer('Stillbirths')
    full_term = fields.Integer('Full Term', help="Full term pregnancies")
    menstrual_history = fields.One2many('oemedical.patient.menstrual_history', 'name', 'Menstrual History')
    mammography_history = fields.One2many('oemedical.patient.mammography_history', 'name', 'Mammography History')
    pap_history = fields.One2many('oemedical.patient.pap_history', 'name', 'PAP smear History')
    prenatal_evaluations = fields.One2many('oemedical.patient.prenatal.evaluation', 'name', 'Prenatal Evaluations')
    colposcopy_history = fields.One2many('oemedical.patient.colposcopy_history', 'name', 'Colposcopy History')
    pregnancy_history = fields.One2many('oemedical.patient.pregnancy', 'name', 'Pregnancies')


class PatientMenstrualHistory(models.Model):

    _name = 'oemedical.patient.menstrual_history'
    _description =  'Menstrual History'

    name = fields.Many2one('oemedical.patient', 'Patient', readonly=True, required=True)
    evaluation = fields.Many2one('oemedical.patient.evaluation', 'Evaluation')
    evaluation_date = fields.Date('Date', help="Evaluation Date",  required=True)
    lmp = fields.Date('LMP', help="Last Menstrual Period", required=True)
    lmp_length = fields.Integer('Length', required=True)
    is_regular = fields.Boolean('Regular')
    dysmenorrhea = fields.Boolean('Dysmenorrhea')
    frequency = fields.Selection([
                            ('amenorrhea', 'amenorrhea'),
                            ('oligomenorrhea', 'oligomenorrhea'),
                            ('eumenorrhea', 'eumenorrhea'),
                            ('polymenorrhea', 'polymenorrhea'),
                            ], 'frequency', sort=False)
    volume = fields.Selection([
                            ('hypomenorrhea', 'hypomenorrhea'),
                            ('normal', 'normal'),
                            ('menorrhagia', 'menorrhagia'),
                            ], 'volume', sort=False)



class PatientMammographyHistory(models.Model):

    _name = 'oemedical.patient.mammography_history'
    _description =  'Mammography History'

    name = fields.Many2one('oemedical.patient', 'Patient', readonly=True, required=True)
    evaluation = fields.Many2one('oemedical.patient.evaluation', 'Evaluation')
    evaluation_date = fields.Date('Date', help=" Date")
    last_mammography = fields.Date('Date', help="Last Mammography", required=True)
    result = fields.Selection([
        ('normal', 'normal'),
        ('abnormal', 'abnormal'),
        ], 'result', help="Please check the lab test results if the module is installed", sort=False)
    comments = fields.Char('Remarks')


class PatientPAPHistory(models.Model):

    _name = 'oemedical.patient.pap_history'
    _description =  'PAP Test History'

    name = fields.Many2one('oemedical.patient', 'Patient', readonly=True, required=True)
    evaluation = fields.Many2one('oemedical.patient.evaluation', 'Evaluation')
    evaluation_date = fields.Date('Date', help=" Date")
    last_pap = fields.Date('Date', help="Last Papanicolau", required=True)
    result = fields.Selection([
                    ('negative', 'Negative'),
                    ('c1', 'ASC-US'),
                    ('c2', 'ASC-H'),
                    ('g1', 'ASG'),
                    ('c3', 'LSIL'),
                    ('c4', 'HSIL'),
                    ('g4', 'AIS'),
                    ], 'result', help="Please check the lab results if the module is installed")
    comments = fields.Char('Remarks')

class PatientColposcopyHistory(models.Model):

    _name = 'oemedical.patient.colposcopy_history'
    _description =  'Colposcopy History'

    name = fields.Many2one('oemedical.patient', 'Patient', readonly=True, required=True)
    evaluation = fields.Many2one('oemedical.patient.evaluation', 'Evaluation')
    evaluation_date = fields.Date('Date', help=" Date")
    last_colposcopy = fields.Date('Date', help="Last colposcopy", required=True)
    result = fields.Selection([
                    ('normal', 'normal'),
                    ('abnormal', 'abnormal'),
                    ], 'result', help="Please check the lab test results if the module is installed", sort=False)
    comments = fields.Char('Remarks')
