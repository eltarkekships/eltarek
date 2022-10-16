from odoo import models, fields


class HrDepartmentInherit(models.Model):
    _inherit = 'hr.department'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')





