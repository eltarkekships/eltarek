from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployee, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                      toolbar=toolbar, submenu=False)
        group_id = self.env['res.users'].has_group('eltarek_access_groups_and_rules.group_show_employee_payroll_time_off_attend')
        doc = etree.XML(res['arch'])
        if not group_id:
            if view_type == 'form':
                nodes = doc.xpath("//form[@string='Employee']")
                for node in nodes:
                    node.set('create', '0')
                    node.set('edit', '0')
                res['arch'] = etree.tostring(doc)
        return res