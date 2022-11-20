from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    number_excuse_per_month = fields.Float()
    max_excuse_period = fields.Float()

class HrLoan(models.Model):
    _inherit = 'hr.loan'

    # def filter(self):
    #     domain = []
    #     loans = self.env['hr.loan'].search([])
    #     ids = []
    #     for exc in loans:
    #         for appr in exc.employee_id.holidays_approvers:
    #             if self.env.uid == appr.approver.user_id.id:
    #                 ids.append(exc.id)
    #
    #     # a = re.search("^admin", self.env.user.login)
    #     print('aaaaaaaa')
    #     if not self.env.user.has_group('sure_portal_hr_self_service.ceo_notification'):
    #         domain = ['|', ('employee_id.user_id', '=', self.env.uid),
    #                   ('id', 'in', ids)]
    #     return {
    #         'name': _("HR Loan"),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'hr.loan',
    #         'view_mode': 'tree,form',
    #         # 'view_type': 'form',
    #         'target': 'current',
    #         'domain': domain,
    #     }
