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

import openerp
from openerp import pooler
from openerp.osv import osv, fields 

import datetime
import os
from openerp.tools.translate import _
import openerp.addons
from openerp.addons import jasper_reports

def jasper_witholding(cr, uid, ids, data, context):
    vat1 = vat2 =vat3 =vat4 = cvat1 = cvat2 =cvat3 =cvat4= ''
    voucher = pooler.get_pool(cr.dbname).get('account.voucher').browse(cr, uid, ids[0])
    partner_id = voucher.partner_id.id
    vat = pooler.get_pool(cr.dbname).get('res.partner').browse(cr, uid, partner_id).vat
    if vat:
        vat = str(vat).split("/")
        vat1 = vat[0]
        vat2 = vat[1]
        vat3 = vat[2]
        vat4 = vat[3]
         
    company_id = pooler.get_pool(cr.dbname).get('res.company')._company_default_get(cr, uid, 'account.voucher',context=context)
    company = pooler.get_pool(cr.dbname).get('res.company').browse(cr, uid, company_id)
    partner_id = company.partner_id.id
    vat = pooler.get_pool(cr.dbname).get('res.partner').browse(cr, uid, partner_id).vat
    if vat:
        vat = str(vat).split("/")
        cvat1 = vat[0]
        cvat2 = vat[1]
        cvat3 = vat[2]
        cvat4 = vat[3]
    invo =''   
    cr.execute("select vl.name  from account_voucher av \
    left outer join account_voucher_line vl on vl.voucher_id = av.id\
    where vl.amount > 0 and av.id IN %s ", (tuple(ids),))
    invoice = cr.dictfetchall()  
    a = len(invoice)
    i = 0
    for inv in invoice:
        i += 1
        if a == 1:
            invo = str(inv['name'])
        else:
            invoice = str(inv['name'])
            if i == a:
                invo += str(invoice)
            else:
                invo += str(invoice) + ' ,'
    return {
        'parameters': {
            'voucher_id': ids[0],
            'vat1' : vat1,
            'vat2' : vat2,
            'vat3' : vat3,
            'vat4' : vat4,
            'cvat1' : cvat1,
            'cvat2' : cvat2,
            'cvat3' : cvat3,
            'cvat4' : cvat4,
            'company': company.name,
            'street': company.street,
            'city': company.city or '',
            'invoice': invo,
            
        }, 
    }

jasper_reports.report_jasper(
    'report.account_voucher1',
    'account.voucher',
    parser=jasper_witholding
)

