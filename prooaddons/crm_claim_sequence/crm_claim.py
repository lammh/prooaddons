# -*- coding: utf-8 -*-
##############################################################################
#
#  OpenERP, CRM Claim Sequence
#  Copyright (c) 2014  Enterprise Objects Consulting
#  All Rights Reserved.
#
#  Authors: Mariano Ruiz <mrsarm@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields

class crm_claim(osv.osv):
    _inherit = 'crm.claim'

    _columns = {
            'number': fields.char('Number', size=64, select=True),
        }

    _defaults = {
            'number': lambda self, cr, uid, context: '/',
        }

    _sql_constraints = [
            ('uniq_number', 'unique(number, company_id)', "The Number must be unique per Company"),
        ]

    def create(self, cr, uid, vals, context=None):
        if not 'number' in vals or vals['number'] == '/':
            vals['number'] = self.pool.get('ir.sequence').get(cr, uid, 'crm.claim')
        return super(crm_claim, self).create(cr, uid, vals, context)

    def copy(self, cr, uid, _id, default={}, context=None):
        default.update({
                'number': self.pool.get('ir.sequence').get(cr, uid, 'crm.claim'),
            })
        return super(crm_claim, self).copy(cr, uid, _id, default, context)

crm_claim()
