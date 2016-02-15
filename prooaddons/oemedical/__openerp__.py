{

    'name': 'OeMedical : Free Health and Hospital Information System',
    'version': '1.0',
    'author': "OeMEdical Team",
    'category': 'Generic Modules/Others',
    'depends': ['base', 'sale', 'purchase', 'account', 'product'],
    'application': True,
    'description': """

About OeMedical
---------------

OeMedical is a multi-user, highly scalable, centralized Electronic
Medical Record (EMR) and Hospital Information System for openERP.

OeMedical provides a free universal Health and Hospital Information System,
so doctors and institutions all over the world,
specially in developing countries will benefit from a centralized,
high quality, secure and scalable system.

OeMedical at a glance:

    * Strong focus in family medicine and Primary Health Care
    
    * Major interest in Socio-economics (housing conditions, substance abuse,
    education...)
    
    * Diseases and Medical procedures standards (like ICD-10 / ICD-10-PCS ...)
    
    * Patient Genetic and Hereditary risks : Over 4200 genes related to
    diseases (NCBI / Genecards)
    
    * Epidemiological and other statistical reports
    
    * 100% paperless patient examination and history taking
    
    * Patient Administration 
    (creation, evaluations / consultations, history ... )
    
    * Doctor Administration
    
    * Lab Administration
    
    * Medicine / Drugs information (vademécum)
    
    * Medical stock and supply chain management
    
    * Hospital Financial Administration
    
    * Designed with industry standards in mind
    
    * Open Source : Licensed under AGPL
    
""",
    "website": "http://launchpad.net/oemedical",
    "licence": "AGPL v3",
    "data": [
        'sequence/oemedical_sequence.xml',
        'oemedical_menu.xml',
        'oemedical_secondary_condition/oemedical_secondary_condition_view.xml',
        'oemedical_pathology_category/oemedical_pathology_category_view.xml',
        'oemedical_signs_and_symptoms/oemedical_signs_and_symptoms_view.xml',
        'product_product/product_product_view.xml',
        'oemedical_physician/oemedical_physician_view.xml',
        'oemedical_directions/oemedical_directions_view.xml',
        'oemedical_insurance/oemedical_insurance_view.xml',
        'res_partner/res_partner_view.xml',
        'oemedical_pathology/oemedical_pathology_view.xml',
        'oemedical_operational_area/oemedical_operational_area_view.xml',
        'oemedical_ethnicity/oemedical_ethnicity_view.xml',
        'oemedical_operational_sector/oemedical_operational_sector_view.xml',
        'oemedical_prescription_order/oemedical_prescription_order_view.xml',
        'oemedical_medicament_category/oemedical_medicament_category_view.xml',
        'oemedical_insurance_plan/oemedical_insurance_plan_view.xml',
        'oemedical_diagnostic_hypothesis/oemedical_diagnostic_hypothesis_view.xml',
        'oemedical_procedure/oemedical_procedure_view.xml',
        'oemedical_medication_template/oemedical_medication_template_view.xml',
        'oemedical_vaccination/oemedical_vaccination_view.xml',
        'oemedical_medication_dosage/oemedical_medication_dosage_view.xml',
        'oemedical_family_member/oemedical_family_member_view.xml',
        'oemedical_hospital_ward/oemedical_hospital_ward_view.xml',
        'oemedical_hospital_or/oemedical_hospital_or_view.xml',
        'oemedical_drug_form/oemedical_drug_form_view.xml',
        'oemedical_patient_medication/oemedical_patient_medication_view.xml',
        'oemedical_patient_evaluation/oemedical_patient_evaluation_view.xml',
        'oemedical_hospital_building/oemedical_hospital_building_view.xml',
        'oemedical_patient/oemedical_patient_view.xml',
        'oemedical_prescription_line/oemedical_prescription_line_view.xml',
        'oemedical_patient_disease/oemedical_patient_disease_view.xml',
        'oemedical_drug_route/oemedical_drug_route_view.xml',
        'oemedical_hospital_unit/oemedical_hospital_unit_view.xml',
        'oemedical_appointment/oemedical_appointment_view.xml',
        'oemedical_specialty/oemedical_specialty_view.xml',
        'oemedical_family/oemedical_family_view.xml',
        'oemedical_hospital_bed/oemedical_hospital_bed_view.xml',
        'oemedical_occupation/oemedical_occupation_view.xml',
        'oemedical_disease_group_members/oemedical_disease_group_members_view.xml',
        'oemedical_medicament/oemedical_medicament_view.xml',
        'oemedical_pathology_group/oemedical_pathology_group_view.xml',
        'oemedical_gynecology_and_obstetrics/oemedical_gynecology_and_obstetrics_view.xml',
        'oemedical_lifestyle/oemedical_lifestyle_view.xml',
        'oemedical_lifestyle/data/recreational_drugs.xml',
        'oemedical_genetics/oemedical_disease_gene_view.xml',
        'oemedical_genetics/data/disease_genes.xml',
        'oemedical_socioeconomics/oemedical_socioeconomics_view.xml',
        'oemedical_lab/oemedical_lab_view.xml',
        'security/ir.model.access.csv',
        'views/theme.xml'
    ],
    "demo": [

    ],
    'test':[
            'test/physician.yml',
            'test/patient.yml',
            'test/partners.yml',
            'test/insurance_plan.yml',
            'test/insurance.yml',
            'test/physician_speciality.yml'
    ],
    'css': [
            'static/src/css/base.css'
    ],
    'js': [

    ],
    'qweb': [

    ],
    "active": False
}
