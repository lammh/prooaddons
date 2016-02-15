# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp import SUPERUSER_ID


import logging
_logger = logging.getLogger(__name__)

class cashbook(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(cashbook, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

    def set_context(self, objects, data, ids, report_type=None):
        obj_cashbook = self.pool.get('oschool.cashbook.wizard')
        obj = obj_cashbook.browse(self.cr, SUPERUSER_ID, ids)

        data = {}
        data['reg_total'] = {}
        data['reg_detail'] = {}
        data['total'] = {}
        data['detail'] = {}
        data['ref'] = []
        data['x_p'] = 0.0
        data['x_n'] = 0.0
        data['x_hand'] = 0.0
        #total remboursé
        data['x_r'] = 0.0
        #total remboursé de la période
        data['x_refund'] = 0.0
        fa=0.0
        date_start = obj.date_start
        date_stop = obj.date_stop
        checkout_wizard = obj.checkout_wizard
        data['user'] = []
        for user in obj.checkout_wizard:
            data['user'].append(user.id)
        data['date_start'] = date_start
        data['date_stop'] = date_stop
        data['checkout_wizard'] = checkout_wizard
        pos_obj = self.pool.get('pos.order')
        order_ids = pos_obj.search(self.cr, self.uid,[
            ('user_id','in',data['user']),
            ('date_order','>=',date_start),
            ('date_order','<=',date_stop)])

        timbre_ids = pos_obj.search(self.cr, self.uid,[
            ('user_id','in',data['user']),
            ('date_order','>=',date_start),
            ('date_order','<=',date_stop),
            ('type','=','Service')])
        orderss = pos_obj.browse(self.cr, self.uid, timbre_ids)
        for o in orderss:
            e = True
            for l in o.lines:
                if l.qty < 0 or l.refunded == True:
                    e = False
            if e:
                fa+=1
        fi = fa * 0.5
        #fi = float(len(timbre_ids)) * 0.5
        data['total']['Timbre Fiscale'] = fi
        orders = pos_obj.browse(self.cr, self.uid, order_ids)
        name=""
        for o in orders:
            for statement in o.statement_ids:
                type_reg = statement.journal_id.name
                #Calcule de total par mode de réglemnt
                if type_reg not in data['reg_total']:
                    data['reg_total'][type_reg] = float(statement.amount)
                else:
                    data['reg_total'][type_reg] += float(statement.amount)

                #Calcule de total par mode de réglemnt par service
                if type_reg not in data['reg_detail']:
                    data['reg_detail'][type_reg] = {}
                    data['reg_detail'][type_reg][o.type] = float(statement.amount)
                else:
                    if o.type not in data['reg_detail'][type_reg]:
                        data['reg_detail'][type_reg][o.type] = 0
                    data['reg_detail'][type_reg][o.type] += float(statement.amount)
            for l in o.lines:
                if l.qty<0:
                    data['ref'].append(l)
                if l.qty>0 and l.refunded == True:
                    data['ref'].append(l)
                name = l.type
                if name not in data['total']:
                    data['total'][name] = float(l.price_subtotal_incl)
                else:
                    data['total'][name] =  data['total'][name] + float(l.price_subtotal_incl)

                if l.order_id.session_id.user_id.name not in data['detail']:
                    data['detail'][l.order_id.session_id.user_id.name] = {}
                    data['detail'][l.order_id.session_id.user_id.name]['detail'] = []
                    data['detail'][l.order_id.session_id.user_id.name]['total'] = float(l.price_subtotal_incl)
                    data['detail'][l.order_id.session_id.user_id.name]['detail'].append(l)
                else:
                    data['detail'][l.order_id.session_id.user_id.name]['detail'].append(l)
                    data['detail'][l.order_id.session_id.user_id.name]['total'] += float(l.price_subtotal_incl)
                if l.state == 'draft':
                    data['x_n'] = data['x_n'] + float(l.price_subtotal_incl)
                else:

                    data['x_p'] = data['x_p'] + float(l.price_subtotal_incl)
                    if l.qty<0:
                            data['x_r'] = data['x_r'] + float(l.price_subtotal_incl)
                    if l.qty>0 and l.refunded == True:
                            data['x_refund'] = data['x_refund'] + float(l.price_subtotal_incl)


            if o.type == "Study":
                data['detail'][o.session_id.user_id.name]['total'] += 0.5
        data['x_hand'] = data['x_p'] + data['x_refund'] + data['x_r'] + fi
        data['x_r'] += data['x_refund']
        return super(cashbook, self).set_context(objects, data, ids, report_type)

class report_cashbook(osv.AbstractModel):
    _name = 'report.oschool.report_cashbook'
    _inherit = 'report.abstract_report'
    _template = 'oschool.report_cashbook'
    _wrapped_report_class = cashbook