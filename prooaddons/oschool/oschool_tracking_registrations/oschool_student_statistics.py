# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import tools

class oschool_student_statistics(models.Model):

    _name = "oschool.next_year_registration"
    _description = "OSchool student Statistics"
    _auto = False

    display_name = fields.Char( string='Student', readonly=True)
    phone = fields.Char(string='Phone', readonly=True)
    phone2 = fields.Char(string='Phone 2', readonly=True)
    mobile = fields.Char(string='Mobile', readonly=True)
    mobile2 = fields.Char(string='Mobile 2', readonly=True)
    email = fields.Char(string='e-Mail', readonly=True)
    company_id = fields.Many2one('res.company',string='Company', readonly=True)
    group_id = fields.Many2one('oschool.groups',string='Group', readonly=True)
    class_id = fields.Many2one('oschool.classes',string='Class', readonly=True)


    def init(self, cr):
        tools.drop_view_if_exists(cr, 'oschool_next_year_registration')
        cr.execute("""
            create or replace view oschool_next_year_registration as (
                SELECT
                    min(r.id) as id,
                    r.display_name as display_name,
                    p.phone as phone,
                    p.phone2 as phone2,
                    p.mobile as mobile,
                    p.mobile2 as mobile2,
                    p.email as email,
                    r.company_id as company_id,
                    r.group_id as group_id,
                    r.class_id as class_id
                FROM res_partner as r, res_partner as p
                WHERE r.parent_id = p.id
                    and r.id in (
                    SELECT id FROM res_partner WHERE is_student = TRUE
                    and active_student = TRUE
                    and allow_registration = TRUE
                    and id not in
                    (select l.student_id from pos_order_line as l, oschool_academic_year as a
                    WHERE l.academic_year_id = a.id
                    AND a.state = 'new' AND type='registration'))
                group by
                    r.display_name,r.name,r.last_name,p.phone,p.phone2,p.mobile,p.mobile2,p.email,p.parent_id,r.company_id,r.group_id,r.class_id
                )""")
