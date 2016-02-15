# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp import SUPERUSER_ID
from openerp.addons.oschool import tools


import logging
_logger = logging.getLogger(__name__)

class payment(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(payment, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

    def set_context(self, objects, data, ids, report_type=None):
        obj_payment = self.pool.get('oschool.payment.wizard')
        payment_obj = obj_payment.browse(self.cr, self.uid, ids)
        academic_year = payment_obj.academic_year_id
        period_id = payment_obj.period_id
        data = {'academic_year': academic_year.name,
                'period_id':period_id.name,
                'study':{}}

        student_ids = self.pool.get('res.partner').search(self.cr, self.uid,[
            ('academic_year_id','=',academic_year.id),
            ('company_id','=',tools.get_default_company(self,self.cr,self.uid)),
            ('active_student','=',True)
        ])

        for student in self.pool.get('res.partner').browse(self.cr,self.uid,student_ids):
            study_ids = self.pool.get('pos.order.line').search(self.cr, self.uid,[
                ('student_id','=',student.id),
                ('period_id','=',period_id.id),
                ('type','=','Study'),
                ('refunded','=',False),
                ('qty','>',0),
            ])
            if study_ids:
                line = self.pool.get('pos.order.line').browse(self.cr,self.uid,study_ids)
                if not line.order_id:
                    if student.group_id.name not in data['study']:
                        data['study'][student.group_id.name] = {}
                        if student.class_id:
                            data['study'][student.group_id.name][student.class_id.name] = []
                            data['study'][student.group_id.name][student.class_id.name].append(student)
                        else:
                            data['study'][student.group_id.name]['NO_CLASS'] = []
                            data['study'][student.group_id.name]['NO_CLASS'].append(student)
                    else:
                        if student.class_id:
                            if student.class_id.name not in data['study'][student.group_id.name]:
                                data['study'][student.group_id.name][student.class_id.name] = []
                                data['study'][student.group_id.name][student.class_id.name].append(student)
                            else:
                                data['study'][student.group_id.name][student.class_id.name].append(student)
                        else:
                            if 'NO_CLASS' not in data['study'][student.group_id.name]:
                                data['study'][student.group_id.name]['NO_CLASS'] = []
                                data['study'][student.group_id.name]['NO_CLASS'].append(student)
                            else:
                                data['study'][student.group_id.name]['NO_CLASS'].append(student)
            else:
                if student.group_id.name not in data['study']:
                    data['study'][student.group_id.name] = {}
                    if student.class_id:
                        data['study'][student.group_id.name][student.class_id.name] = []
                        data['study'][student.group_id.name][student.class_id.name].append(student)
                    else:
                        data['study'][student.group_id.name]['NO_CLASS'] = []
                        data['study'][student.group_id.name]['NO_CLASS'].append(student)
                else:
                    if student.class_id:
                        if student.class_id.name not in data['study'][student.group_id.name]:
                            data['study'][student.group_id.name][student.class_id.name] = []
                            data['study'][student.group_id.name][student.class_id.name].append(student)
                        else:
                            data['study'][student.group_id.name][student.class_id.name].append(student)
                    else:
                        if 'NO_CLASS' not in data['study'][student.group_id.name]:
                            data['study'][student.group_id.name]['NO_CLASS'] = []
                            data['study'][student.group_id.name]['NO_CLASS'].append(student)
                        else:
                            data['study'][student.group_id.name]['NO_CLASS'].append(student)
            
        return super(payment, self).set_context(objects, data, ids, report_type)

class payment_report(osv.AbstractModel):
    _name = 'report.oschool.payment_report'
    _inherit = 'report.abstract_report'
    _template = 'oschool.payment_report'
    _wrapped_report_class = payment




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
