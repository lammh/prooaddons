# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name' : 'Treasury', # 
    'version' : '3.0',
    'category': 'Accounting',
    'description' : 'Treasury documents',
    'author' : 'Digitec',
    'category' : 'Generic Modules/Accounting',
    'depends' : ['account_voucher', 'hr'],
    'data' : [
        'res_bank_data.xml',
        'treasury_type_data.xml',
        'security/ir.model.access.csv',
        'treasury_view.xml',
        'vesement_sequence.xml',
        'report_menus.xml',
        'vesement_view.xml',
        'voucher_view.xml',
        'partner_view.xml',
    ],
    'active': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
