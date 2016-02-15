# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp import SUPERUSER_ID
from datetime import date, datetime
from datetime import timedelta



import logging
_logger = logging.getLogger(__name__)

class today_payment(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
       super(today_payment, self).__init__(cr, uid, name, context=context)
       time = datetime.now()+timedelta(hours=1,minutes=00)
       self.localcontext.update({
            'value': time,
       })
       self.context = context


    def set_context(self, objects, data, ids, report_type=None):
        data = {}
        data['reg_total'] = {}
        data['reg_detail'] = {}
        data['total'] = {}
        data['detail'] = {}
        data['ref'] = []
        #total payé
        data['x_p'] = 0.0
        #total non payé
        data['x_n'] = 0.0
        #total remboursé
        data['x_r'] = 0.0
        #total remboursé de jour
        data['x_refund'] = 0.0
        #total en main
        data['x_hand'] = 0.0
        #variable pour le calcul de nombre de facture contenant le timbre fiscale
        fa = 0.0
        today = date.today()
        data['today'] = str(today)
        data['user'] = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name
        pos_obj = self.pool.get('pos.order')
        order_ids = pos_obj.search(self.cr, self.uid,[('user_id','=',self.uid),('date_order','ilike','%'+str(today)+'%')])
        timbre_ids = pos_obj.search(self.cr, self.uid,[
            ('user_id','=',self.uid),
            ('date_order','ilike','%'+str(today)+'%'),
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
        name = ""
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
                if l.qty>0 and l.refunded == False:
                    name = l.type
                    if name not in data['total']:
                        data['total'][name] = float(l.price_subtotal_incl)
                        data['detail'][name] = []
                        data['detail'][name].append(l)
                    else:
                        data['total'][name] =  data['total'][name] + float(l.price_subtotal_incl)
                        data['detail'][name].append(l)
                    if l.state == 'draft':
                        data['x_n'] = data['x_n'] + float(l.price_subtotal_incl)
                    else:
                        if l.qty>0 and l.refunded == False:
                            data['x_p'] = data['x_p'] + float(l.price_subtotal_incl)
                        if l.qty<0:
                            data['x_r'] = data['x_r'] + float(l.price_subtotal_incl)

                else:
                    if l.qty<0:
                        data['x_r'] = data['x_r'] + float(l.price_subtotal_incl)
                    data['ref'].append(l)
                    if l.qty>0 and l.refunded == True:
                            data['x_refund'] = data['x_refund'] + float(l.price_subtotal_incl)
        data['x_hand'] = data['x_p'] + data['x_refund'] + data['x_r'] + fi
        data['x_r'] += data['x_refund']

        return super(today_payment, self).set_context(objects, data, ids, report_type)

class today_payment_report(osv.AbstractModel):
    _name = 'report.oschool.today_payment_report'
    _inherit = 'report.abstract_report'
    _template = 'oschool.today_payment_report'
    _wrapped_report_class = today_payment


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: