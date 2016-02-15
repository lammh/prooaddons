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
from openerp import tools, api
import openerp
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class oschool_responsible(osv.osv):
    _inherit = 'res.partner'

    def payment_responsible(self, cr, uid, ids, context=None):
        if not ids: return []
        current_session_ids = self.pool.get('pos.session').search(cr, uid, [
        ('state', '!=', 'closed'),
        ('user_id', '=', uid)], context=context)
        if not current_session_ids:
            raise osv.except_osv(_('Error!'), _('Open a session first.'))
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_payment_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': _("Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_responsible_id': inv.id,
            }
        }

    def extra_payment_responsible(self, cr, uid, ids, context=None):
        if not ids: return []
        current_session_ids = self.pool.get('pos.session').search(cr, uid, [
        ('state', '!=', 'closed'),
        ('user_id', '=', uid)], context=context)
        if not current_session_ids:
            raise osv.except_osv(_('Error!'), _('Open a session first.'))
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_extra_payment_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': _("Extra Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.extra.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_responsible_id': inv.id,
            }
        }
    def study_payment_responsible(self, cr, uid, ids, context=None):
        if not ids: return []
        current_session_ids = self.pool.get('pos.session').search(cr, uid, [
        ('state', '!=', 'closed'),
        ('user_id', '=', uid)], context=context)
        if not current_session_ids:
            raise osv.except_osv(_('Error!'), _('Open a session first.'))
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_study_payment_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': _("Extra Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.study.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_responsible_id': inv.id,
            }
        }

    #*********** total responsible payment on period *****************
    def total_period_payment_responsible(self, cr, uid, ids, context=None):
        #if not ids: return []
        #current_session_ids = self.pool.get('pos.session').search(cr, uid, [
        #('state', '!=', 'closed'),
        #('user_id', '=', uid)], context=context)
        #if not current_session_ids:
        #    raise osv.except_osv(_('Error!'), _('Open a session first.'))
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_period_payment_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': _("Total Period Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.period.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_responsible_id': inv.id,
            }
        }



    @api.multi
    def onchange_state2(self, state_id2):
        if state_id2:
            state = self.env['res.country.state'].browse(state_id2)
            return {'value': {'country_id2': state.country_id.id}}
        return {}

    def _get_nbre_child(self, cr, uid, ids, field_names, arg=None, context=None, query='', query_params=()):
        res = {}
        for id in ids:
            child = self.search(cr, SUPERUSER_ID,[('parent_id','=',id),('active_student','=',True)])
            res[id] = str(len(child))
        return res


    _columns = {
        'is_responsible': fields.boolean('Is Responsible'),
        'cash': fields.boolean('Cash'),
        'last_name': fields.char(size=128, string='Last Name'),
        'name2': fields.char('Responsible 2 Firstname'),
        'last_name2': fields.char(size=128, string='Responsible 2 Lastname 2'),
        'function2': fields.char('Responsible 2 Job Position'),
        'phone2': fields.char('Responsible 2 Tel. 1'),
        'mobile2': fields.char('Responsible 2 Tel. 2'),
        'email2': fields.char('Responsible 2 Email'),
        'state_id2': fields.many2one("res.country.state", 'State 2', ondelete='restrict'),
        'city2': fields.char('City 2'),
        'zip2': fields.char('Zip 2', size=24, change_default=True),
        'country_id2': fields.many2one('res.country', 'Country 2', ondelete='restrict'),
        'image2': fields.binary("Image 2", help= "This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'history_payments': fields.one2many('pos.order', 'partner_id', string='History Payment'),
        'nbre_child': fields.function(_get_nbre_child, type='char', string='Number of active children')
    }

    def _get_default_image_oschool(self, cr, uid, context=None):
        img_path = openerp.modules.get_module_resource(
            'oschool', 'static/src/img', 'avatar.png' if context.get('default_is_responsible') else 'student.png')
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if context.get('default_is_responsible'):
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))

    def _get_default_image_identity(self, cr, uid, context=None):
        img_path = openerp.modules.get_module_resource(
            'oschool', 'static/src/img', 'identity.png')
        with open(img_path, 'rb') as f:
            image = f.read()
        return tools.image_resize_image_big(image.encode('base64'))

    _defaults = {
        'image': _get_default_image_oschool,
        'image2': _get_default_image_identity,
    }
    _sql_constraints = [
        ('partner_ref_unique','unique(ref)', 'Ref already exists'),
    ]


oschool_responsible()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: