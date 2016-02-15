# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import tools
from openerp.osv import osv, fields
import time
from dns.rdatatype import NULL

class statement_extrait_report(osv.osv_memory):
    _name = 'statement.extrait.report'
    _description = 'Report Statement General'

    _columns = {
        'name': fields.many2one('account.account', 'Account'),
        'date_start': fields.date('Start date', required=True),
        'date_end': fields.date('End date', required=True),
    }

    _defaults = {
        'name': lambda obj, cr, uid, context: context.get('active_id', None),
        'date_start': lambda *a: time.strftime('%Y-%m-01'),
        'date_end': lambda *a: time.strftime('%Y-12-31'),
    }

    def launch(self, cr, uid, ids, context=None):
        """
        Launch the report, and pass each value in the form as parameters
        """

        wiz = self.browse(cr, uid, ids, context=context)[0]
        cr.execute("""\
                    SELECT sum(debit),sum(credit) FROM public.account_move_line WHERE 
                    account_move_line.account_id = %s AND 
                    account_move_line.date >= '%s' AND 
                    account_move_line.date < '%s'
                    """  % (wiz.name.id, '20150101',wiz.date_start,))        
        result = cr.fetchall()
        if result[0][1] is not None:
            credit_init = str(result[0][1])
        else:
            credit_init = str(0)
        if result[0][0] is not None:
            debit_init = str(result[0][0])
        else:
            debit_init = str(0)

        
       
        data = {}
        data['parameters'] = {
            'partner_id': wiz.name.id,
            'date_start': wiz.date_start,
            'date_end': wiz.date_end,
            'compte_num': wiz.name.code,
            'compte_name': wiz.name.name,
            'param_credit': credit_init,
            'param_debit': debit_init,               
        }

        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account_statment_extrait',
                'datas': data,
        }


statement_extrait_report()

