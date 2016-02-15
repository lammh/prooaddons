# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import time
from openerp.exceptions import ValidationError
from openerp.osv import osv
from openerp.addons.oschool import tools

class oschool_event(models.Model):

    _inherit="product.template"

    academic_year = fields.Many2one('oschool.academic_year', ondelete='cascade', string="Academic year")
    event_start_date_registration = fields.Date(string='Start Registration Date')
    event_stop_date_registration = fields.Date(string='End Registration Date')
    event_date_start = fields.Date(string='Start Date')
    event_date_stop = fields.Date(string='End Date')
    event_place_number = fields.Integer(string="Number of places")
    company_id = fields.Many2one('res.company', 'Company')

    def create(self, cr, uid, vals, context=None):

        if vals.has_key('categ_id'):
            oschool_event_product_category_obj = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'oschool_event_product_category')[1]
            if vals['categ_id'] == oschool_event_product_category_obj:
                company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
                property_account_income = self.pool.get('account.account').search(cr, uid, [('code', '=', '7050005'),('company_id','=',company_id)])
                if not property_account_income:
                    raise ValidationError("There is not account with code 7050005")
                vals['property_account_income'] = property_account_income[0]
        return super(oschool_event, self).create(cr, uid, vals, context=context)
    _defaults = {
        'company_id': tools.get_default_company,
    }

class event_registration(models.Model):
    _inherit = 'pos.order.line'

    def registration_event_refund(self, cr, uid, ids, context=None):
        if not ids:
            return []
        clone_list = []
        inv = self.browse(cr, uid, ids[0], context=context)
        if not inv.order_id:
            student = inv.student_id
            self.unlink(cr, uid,[inv.id])
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_student_form')

            return {
            'name': _("Oschool Student"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': student.id,
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
        }
        if inv.order_id and inv.order_id.state == 'draft':
            raise osv.except_osv(_('Warning!'), _('Please select another line because it not payed.'))
        if inv.refunded:
            raise osv.except_osv(_('Warning!'), _('Please select another line because it Refunded.'))
        if inv.qty < 0:
            clone_list.append(inv.order_id.id)
        else:
            current_session_ids = self.pool.get('pos.session').search(cr, uid, [
            ('state', '!=', 'closed'),
            ('user_id', '=', uid)], context=context)
            if not current_session_ids:
                raise osv.except_osv(_('Error!'), _('To return product(s), you need to open a session that will be used to register the refund.'))

            order = inv.order_id
            clone_id = self.pool.get('pos.order').copy(cr, uid, order.id, {
                'name': order.name + ' REFUND', # not used, name forced by create
                'session_id': current_session_ids[0],
                'date_order': time.strftime('%Y-%m-%d %H:%M:%S'),
                'lines' : False
            }, context=context)
            self.copy(cr, uid, inv.id, {
                'qty': -inv.qty, # not used, name forced by create
                'subscriber': False,
                'order_id':clone_id
            }, context=context)
            self.write(cr, uid, inv.id, {'refunded': True, 'subscriber': False}, context=context)
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_refund_pos_form')

            return {
                'name': _("Refund Registration"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': clone_id,
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'pos.order',
                'type': 'ir.actions.act_window',
                'nodestroy': False,
                'target': 'new',
                'context': {
                    'subscription_month': inv.period_id.code,
                }
            }



    event_price = fields.Float(related="price_unit", string="Price")

    def create(self, cr, uid, values, context=None):
         if 'type' in values:
            if values['type'] == 'event':
                product = self.pool.get('product.product').browse(cr, uid, values['product_id'])
                values['academic_year_id'] = product.academic_year.id
         return super(event_registration, self).create(cr, uid, values, context=context)


    @api.onchange('product_id')
    def set_remaining_place(self):
        if self.product_id:
            event_registered_student = self.env['pos.order.line'].search([('product_category_id', '=', self.product_id.categ_id[0].id), ('academic_year_id', '=', self.product_id.academic_year[0].id), ('qty', '!=', -1)])
            self.remaining_places = self.product_id.event_place_number - len(event_registered_student)
            self.event_price = self.product_id.list_price
            self.price_unit = self.product_id.list_price
            if( self.remaining_places == 0):
                self.product_id = ""
                return {'value': {'product_id': False}, 'warning': {'title': _('Warning!'), 'message': _('There is no more places available.')}}


    @api.onchange('student_id')
    def check_user_registred(self):
        if self.student_id:
            if self.product_id:
                student_registered = self.env['pos.order.line'].search([('product_id', '=', self.product_id.id), ('academic_year_id', '=', self.product_id.academic_year[0].id),('student_id', '=', self.student_id.id)])
                if(len(student_registered)  > 0):
                    self.student_id = ""
                    return {'warning': {'title': _('Warning!'), 'message': _('Student already registered for this event.')}}


class oschool_event_student(models.Model):
    _inherit = 'res.partner'

    event_registration_ids = fields.One2many('pos.order.line', 'student_id', string='Registration List',domain=[('type' , '=', 'event')])

