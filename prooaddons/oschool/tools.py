# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import _


def get_default_company(self, cr, uid, context=None):
    company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
    if not company_id:
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
    return company_id

