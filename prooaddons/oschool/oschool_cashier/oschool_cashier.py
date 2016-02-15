# -*- coding: utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
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
#/#############################################################################
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID

class oschool_cashier(osv.osv):
    _inherit = 'res.users'

    _columns = {
        'is_cashier': fields.boolean('Is Cashier'),
        'location_id': fields.many2one('stock.location','Cashier Location'),
    }

    def create_location(self, cr, uid, vals, context=None):
        location = {
            'name': vals['name'],
            'location_id': self.pool.get('pos.config')._get_default_location(cr, uid, context=context),
        }
        return self.pool.get('stock.location').create(cr, uid, location)

    def create(self, cr, uid, vals, context=None):
        if not 'location_id' in vals or not vals['location_id']:
            vals.update({'location_id': self.create_location(cr, SUPERUSER_ID, vals, context)})
        return super(oschool_cashier, self).create(cr, uid, vals, context)

oschool_cashier()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
