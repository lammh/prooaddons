# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    'name': "Stock Picking Report",
    'version': '1.0',
    'sequence': 20,
    'category': 'Warehouse Management',
    'description': """Add a global discount in account invoice""",
    'author': 'Digitec',
    'website': 'http://www.digitecsys.com',
    'license': 'AGPL-3',
    "depends" : ['stock_valued_picking_report'],
    "data" : [
        'picking_report.xml',
        'picking_report_valued.xml',
        ],
    "demo_xml" : [],
    "active": False,
    "installable": True,
}
