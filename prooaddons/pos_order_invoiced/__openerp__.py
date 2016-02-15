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
    'name' : 'Point of sale Order invoiced', # 
    'version' : '3.0',
    'category': 'Customer Relationship Management',
    'description' : 'Point of sale Order Invoiced',
    'author' : 'ERP SYSTEMS',
    'category' : 'Generic Modules/Accounting',
    'depends' : ['point_of_sale'],
    'data' : ['wizard/pos_invoiced_view.xml'],
    'active': False 
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
