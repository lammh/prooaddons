# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import tools

class oschool_registrations_report(models.Model):

    _name = "report.oschool.registrations"
    _description = "OSchool registrations Statistics"
    _auto = False

    date = fields.Datetime(string='Date Order', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    student_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    price_total = fields.Float(string='Total Price', readonly=True)
    product_qty = fields.Integer(string='Product Quantity', readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    academic_year_id = fields.Many2one('oschool.academic_year', string="Academic year", readonly=True)
    nbr = fields.Integer(string= '# of Lines', readonly=True)
    state = fields.Selection([('draft', 'New'), ('paid', 'Payed'), ('done', 'Payed'), ('invoiced', 'Payed'), ('cancel', 'Cancelled')], string='Status')
    average_price = fields.Float(string='Average Price', readonly=True, group_operator="avg")
    statement_id = fields.Integer(string="Statement", readonly=True)
    bank_journal_id = fields.Many2one("account.journal", string="journal", readonly=True)
    class_id = fields.Many2one('oschool.classes', string='Class', readonly=True)
    group_id = fields.Many2one('oschool.groups', string='Group',readonly=True)
    company_id = fields.Many2one('res.company', string='Company',readonly=True)

    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_oschool_registrations')
        cr.execute("""
            create or replace view report_oschool_registrations as (
                select
                    min(l.id) as id,
                    l.academic_year_id as academic_year_id,
                    l.class_id as class_id,
                    l.group_id as group_id,
                    count(*) as nbr,
                    s.date_order as date,
                    sum(l.qty * u.factor) as product_qty,
                    sum(l.qty * l.price_unit) as price_total,
                    sum((l.qty * l.price_unit) * (l.discount / 100)) as total_discount,
                    (sum(l.qty*l.price_unit)/sum(l.qty * u.factor))::decimal as average_price,
                    sum(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') as int)) as delay_validation,
                    s.partner_id as partner_id,
                    s.student_id as student_id,
                    s.state as state,
                    s.user_id as user_id,
                    s.location_id as location_id,
                    s.company_id as company_id,
                    s.sale_journal as journal_id,
                    l.product_id as product_id,
                    absl.journal_id as bank_journal_id,
                    pt.categ_id as product_categ_id,
                    absl.statement_id as statement_id
                from pos_order_line as l
                    left join pos_order s on (s.id=l.order_id)
                    left join product_product p on (p.id=l.product_id)
                    left join product_template pt on (pt.id=p.product_tmpl_id)
                    left join product_uom u on (u.id=pt.uom_id)
                    left join account_bank_statement_line absl on (absl.pos_statement_id=l.order_id)
                    left join account_journal aj on (aj.id=absl.journal_id)
                where l.type='registration'
                group by
                    s.date_order, s.partner_id,s.student_id,s.state, pt.categ_id,l.class_id,l.group_id,
                    s.user_id,s.location_id,s.company_id,s.sale_journal,l.product_id,l.academic_year_id,absl.statement_id,absl.journal_id,s.create_date
                having
                    sum(l.qty * u.factor) != 0)""")
