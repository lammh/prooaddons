# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi. Copyright Camptocamp SA
#    Donors: Hasa Sàrl, Open Net Sàrl and Prisme Solutions Informatique SA
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

import time
from datetime import datetime
import base64

from openerp.osv import osv, fields
from openerp import pooler
from openerp.tools.translate import _

import re

TRANS=[
    (u'é','e'),
    (u'è','e'),
    (u'à','a'),
    (u'ê','e'),
    (u'î','i'),
    (u'ï','i'),
    (u'â','a'),
    (u'ä','a'),
]

def tr(string_in):
    try:
        string_in= string_in.decode('utf-8')
    except:
        # If exception => then just take the string as is
        pass
    for k in TRANS:
        string_in = string_in.replace(k[0],k[1])
    try:
        res= string_in.encode('ascii','replace')
    except:
        res = string_in
    return res


class record:
    def __init__(self, global_context_dict):
        for i in global_context_dict:
            global_context_dict[i] = global_context_dict[i] \
                    and tr(global_context_dict[i])
        self.fields = []
        self.global_values = global_context_dict
        self.pre = {
            'padding': '',
            'seg_num1': '01',
            'seg_num2': '02',
            'seg_num3': '03',
            'seg_num4': '04',
            'seg_num5': '05',
            'flag': '0',
            'zero4': '          '
        }
        self.post={'date_value_hdr': '000000', 'type_paiement': '0'}
        self.init_local_context()

    def init_local_context(self):
        """
        Must instanciate a fields list, field = (name,size)
        and update a local_values dict.
        """
        raise _('not implemented')

    def generate(self):
        res=''
        for field in self.fields :
            if self.pre.has_key(field[0]):
                value = self.pre[field[0]]
            elif self.global_values.has_key(field[0]):
                value = self.global_values[field[0]]
            elif self.post.has_key(field[0]):
                value = self.post[field[0]]
            else :
                pass
            try:
                res = res + c_ljust(value, field[1])
            except :
                pass
        return res


class record_cnss(record):
    def init_local_context(self):
        self.fields=[
            ('num_employeur', 8),
            ('codexp', 2),
            ('ssnid', 10),
            ('trimestre', 1),
            ('annee', 2),
            ('amount', 8),
            ('identification_id', 6),
            ('identite', 34),
            ('page', 3),
            ('ligne', 2),
            ('zero4', 4),
            ('newline', 1)
        ]
        self.pre.update( {
            'newline': '\r\n',
        })

def c_ljust(s, size):
    """
    check before calling ljust
    """
    s= s or ''
    if len(s) > size:
        s= s[:size]
    s = s.decode('utf-8').encode('latin1','replace').ljust(size)
    return s

def _create_cnss(self, cr, uid, data, context=None):
    v = {}
    dta = ''

    pool = pooler.get_pool(cr.dbname)
    declar_obj = pool.get('hr.cnss')
    attachment_obj = pool.get('ir.attachment')
    if context is None:
        context = {}

    declar = declar_obj.browse(cr, uid, data['id'], context=context)
    v['num_employeur'] = str(declar.company_id.company_cnss).zfill(8)
    v['codexp']= str(declar.codexp)[2:]
    v['trimestre'] = str(declar.period)
    v['annee'] = str(declar.year)[2:]

    for pline in declar.detail_ids:
        v['page']= str(pline.name).zfill(3)
        v['ligne']= str(pline.line).zfill(2)
        v['ssnid'] =  str(pline.sec_nbr or '0').zfill(10)
        v['identite'] =  str(pline.emp_name).ljust(34, ' ')
        v['identification_id'] =  str(pline.matricule).zfill(6)
        v['amount'] = str(pline.amount * 100).replace(".", "").zfill(8)

        record_type = record_cnss

        dta_line = record_type(v).generate()

        dta = dta + dta_line

    dta_data = base64.encodestring(dta)
    attachment_obj.create(cr, uid, {
        'name': declar.name,
        'datas': dta_data,
        'datas_fname': '%s.txt'%declar.name,
        'res_model': 'hr.cnss',
        'res_id': data['id'],
        }, context=context)
    return dta_data

class create_cnss_wizard(osv.osv):
    _inherit="hr.cnss"

    def action_approve(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if isinstance(ids, list):
            req_id = ids[0]
        else:
            req_id = ids
        current = self.browse(cr, uid, req_id, context)
        data = {}

        data['id'] = ids[0]
        dta_file = _create_cnss(self, cr, uid, data, context)
        self.write(cr, uid, req_id, {'state':'pending'}, context=context)
        return True

create_cnss_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
