from openerp import models,fields


class OeMedicalPatientEvaluation(models.Model):
    _name='oemedical.patient.evaluation'
    _rec_name='patient_id'

    patient_id = fields.Many2one('oemedical.patient', 'Patient')
    information_source = fields.Char(size=256, string='Source',
        help="Source of" "Information, eg : Self, relative, friend ...")
    info_diagnosis = fields.Text(
        string='Presumptive Diagnosis: Extra Info')
    orientation = fields.Boolean(string='Orientation',
        help='Check this box if the patient is disoriented in time and/or'\
        ' space')
    weight = fields.Float(string='Weight',
                           help='Weight in Kilos')
    evaluation_type = fields.Selection([
        ('a', 'Ambulatory'),
        ('e', 'Emergency'),
        ('i', 'Inpatient'),
        ('pa', 'Pre-arranged appointment'),
        ('pc', 'Periodic control'),
        ('p', 'Phone call'),
        ('t', 'Telemedicine'),
    ], string='Type')
    malnutrition = fields.Boolean(string='Malnutrition',
    help='Check this box if the patient show signs of malnutrition. If'\
    ' associated  to a disease, please encode the correspondent disease'\
    ' on the patient disease history. For example, Moderate'\
    ' protein-energy malnutrition, E44.0 in ICD-10 encoding')
    actions = fields.One2many('oemedical.directions',
                               'evaluation_id', string='Procedures',
                               help='Procedures / Actions to take')
    height = fields.Float(string='Height',
                           help='Height in centimeters, eg 175')
    dehydration = fields.Boolean(string='Dehydration',
        help='Check this box if the patient show signs of dehydration. If'\
        ' associated  to a disease, please encode the  correspondent disease'\
        ' on the patient disease history. For example, Volume Depletion, E86'\
        ' in ICD-10 encoding')
    tag = fields.Integer(string='Last TAGs',
        help='Triacylglycerol(triglicerides) level. Can be approximative')
    tremor = fields.Boolean(string='Tremor',
       help='If associated  to a disease, please encode it on the patient'\
       ' disease history')
    present_illness = fields.Text(string='Present Illness')
    evaluation_date = fields.Many2one('oemedical.appointment',
                                       string='Appointment',
        help='Enter or select the date / ID of the appointment related to'\
             ' this evaluation')
    evaluation_start = fields.Datetime(string='Start', required=True)
    loc = fields.Integer(string='Level of Consciousness')
    user_id = fields.Many2one('res.users', string='Last Changed by',
                               readonly=True)
    mood = fields.Selection([
        ('n', 'Normal'),
        ('s', 'Sad'),
        ('f', 'Fear'),
        ('r', 'Rage'),
        ('h', 'Happy'),
        ('d', 'Disgust'),
        ('e', 'Euphoria'),
        ('fl', 'Flat'),
    ], string='Mood')
    doctor = fields.Many2one('oemedical.physician', string='Doctor',
                              readonly=True)
    knowledge_current_events = fields.Boolean(
        string='Knowledge of Current Events',
        help='Check this box if the patient can not respond to public'\
        ' notorious events')
    next_evaluation = fields.Many2one('oemedical.appointment',
                                       string='Next Appointment',)
    signs_and_symptoms = fields.One2many('oemedical.signs_and_symptoms',
                                          'evaluation_id',
                                          string='Signs and Symptoms',
                                        help="Enter the Signs and Symptoms \
                                    for the patient in this evaluation.")
    loc_motor = fields.Selection([
        ('1', 'Makes no movement'),
        ('2', 'Extension to painful stimuli - decerebrate response -'),
        ('3',
         'Abnormal flexion to painful stimuli (decorticate response)'),
        ('4', 'Flexion / Withdrawal to painful stimuli'),
        ('5', 'Localizes painful stimuli'),
        ('6', 'Obeys commands'),
    ], string='Glasgow - Motor')
    reliable_info = fields.Boolean(string='Reliable',
                                    help="Uncheck this option" \
    "if the information provided by the source seems not reliable")
    systolic = fields.Integer(string='Systolic Pressure')
    vocabulary = fields.Boolean(string='Vocabulary',
    help='Check this box if the patient lacks basic intelectual capacity,'\
    ' when she/he can not describe elementary objects')
    praxis = fields.Boolean(string='Praxis',
          help='Check this box if the patient is unable to make voluntary'\
          'movements')
    hip = fields.Float(string='Hip',
                        help='Hip circumference in centimeters, eg 100')
    memory = fields.Boolean(string='Memory',
        help='Check this box if the patient has problems in short or long'\
        ' term memory')
    abstraction = fields.Boolean(string='Abstraction',
        help='Check this box if the patient presents abnormalities in'\
        ' abstract reasoning')
    patient_id = fields.Many2one('oemedical.patient', string='Patient',)
    derived_from = fields.Many2one('oemedical.physician',
                                    string='Derived from',
                                    help='Physician who derived the case')
    specialty = fields.Many2one('oemedical.specialty',
                                 string='Specialty',)
    loc_verbal = fields.Selection([
        ('1', 'Makes no sounds'),
        ('2', 'Incomprehensible sounds'),
        ('3', 'Utters inappropriate words'),
        ('4', 'Confused, disoriented'),
        ('5', 'Oriented, converses normally'),
    ], string='Glasgow - Verbal')
    glycemia = fields.Float(string='Glycemia',
                    help='Last blood glucose level. Can be approximative.')
    head_circumference = fields.Float(string='Head Circumference',
                                       help='Head circumference')
    bmi = fields.Float(string='Body Mass Index')
    respiratory_rate = fields.Integer(string='Respiratory Rate',
                help='Respiratory rate expressed in breaths per minute')
    derived_to = fields.Many2one('oemedical.physician',
                                  string='Derived to',
                    help='Physician to whom escalate / derive the case')
    hba1c = fields.Float(string='Glycated Hemoglobin',
                    help='Last Glycated Hb level. Can be approximative.')
    violent = fields.Boolean(string='Violent Behaviour',
       help='Check this box if the patient is agressive or violent at the'\
       ' moment')
    directions = fields.Text(string='Plan')
    evaluation_summary = fields.Text(string='Evaluation Summary')
    cholesterol_total = fields.Integer(string='Last Cholesterol')
    diagnostic_hypothesis = fields.One2many(
        'oemedical.diagnostic_hypothesis',
        'evaluation_id', string='Hypotheses / DDx',
        help='Presumptive Diagnosis. If no diagnosis can be made'\
        ', encode the main sign or symptom.')
    judgment = fields.Boolean(string='Jugdment',
    help='Check this box if the patient can not interpret basic scenario'\
    ' solutions')
    temperature = fields.Float(string='Temperature',
                                help='Temperature in celcius')
    osat = fields.Integer(string='Oxygen Saturation',
                           help='Oxygen Saturation(arterial).')
    secondary_conditions = fields.One2many(
        'oemedical.secondary_condition', 'evaluation_id',
        string='Secondary Conditions',
        help="Other, Secondary conditions found on the patient")
    evaluation_endtime = fields.Datetime(string='End', required=True)
    notes = fields.Text(string='Notes')
    calculation_ability = fields.Boolean(string='Calculation Ability',
        help='Check this box if the patient can not do simple arithmetic'\
        ' problems')
    bpm = fields.Integer(string='Heart Rate',
                          help='Heart rate expressed in beats per minute')
    chief_complaint = fields.Char(size=256, string='Chief Complaint',
                                   required=True,
                                   help='Chief Complaint')
    loc_eyes = fields.Selection([
        ('1', 'Does not Open Eyes'),
        ('2', 'Opens eyes in response to painful stimuli'),
        ('3', 'Opens eyes in response to voice'),
        ('4', 'Opens eyes spontaneously'),
    ], string='Glasgow - Eyes')
    abdominal_circ = fields.Float(string='Waist')
    object_recognition = fields.Boolean(string='Object Recognition',
      help='Check this box if the patient suffers from any sort of gnosia'\
      ' disorders, such as agnosia, prosopagnosia ...')
    diagnosis = fields.Many2one('oemedical.pathology',
                                 string='Presumptive Diagnosis',)
    whr = fields.Float(string='WHR', help='Waist to hip ratio')
    ldl = fields.Integer(string='Last LDL',
                help='Last LDL Cholesterol reading. Can be approximative')
    notes_complaint = fields.Text(string='Complaint details')
    hdl = fields.Integer(string='Last HDL')
    diastolic = fields.Integer(string='Diastolic Pressure')
