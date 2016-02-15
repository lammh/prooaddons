# -*- encoding: utf-8 -*-
##############################################################################
#
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons import jasper_reports
from openerp.osv import osv,fields 
import openerp.pooler
import datetime

 
 
def jasper_declaration_trim_cnss_parser( cr, uid, ids, data, context ):
	return {
		'parameters': {
			'id_cnss': ids[0],
		},
	}

jasper_reports.report_jasper(
	'report.hr_cnss_statement',
	'hr.cnss',
	parser=jasper_declaration_trim_cnss_parser
)
 


 
