from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime

class hr_note(osv.osv):
    
    _name = 'hr.note'
    _columns = {
        'name': fields.char('Note', size=2, required=True),
        'note':fields.float('Rating',digits_compute=dp.get_precision('Account'), required=True),
    }
hr_note()

class hr_employee_note(osv.osv):
    
    _name = 'hr.employee.note'
    _order = 'year desc'
    _columns = {
        'name': fields.many2one('hr.employee', 'Employee'),
        'note':fields.many2one('hr.note', 'Note'),
        'year':fields.integer('Year', size=4),
    }
    _defaults = {
        'year': int(datetime.now().year),
    }
    
hr_employee_note()    

class hr_employee(osv.osv):
    
    _inherit = 'hr.employee'
    _columns = {
        'note_ids': fields.one2many('hr.employee.note', 'name', 'Employee Note'),
                }
hr_employee()

        
