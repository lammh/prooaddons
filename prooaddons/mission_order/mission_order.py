# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import models, fields, api, _

class fleet_vehicle(models.Model):
    _name = "fleet.vehicle"

    name = fields.Char(string="vehicle", required=True)

class mission_order(models.Model):
    _name = "mission.order"
    _order = 'name desc'

    name = fields.Char(string="Ref", readonly=True)
    date_start = fields.Datetime(string="Date Start", required=True)
    date_end = fields.Datetime(string="Date End", required=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    vehicle_id  = fields.Many2one("fleet.vehicle", required=True)
    location_id = fields.Many2one("stock.location", string="Location", required=True, domain="[('usage', '=', 'internal')]")
    route = fields.Char(string="Route")

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'mission.order') or '/'
        return super(mission_order, self).create(cr, uid, vals, context=context)