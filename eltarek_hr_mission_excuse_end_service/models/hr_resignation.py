# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class HrResgnation(models.Model):
    _inherit = 'hr.resignation'


    # def filter(self):
    #     domain = []
    #     resignations = self.env['hr.resignation'].search([])
    #     ids = []
    #     for exc in resignations:
    #         for appr in exc.employee_id.holidays_approvers:
    #             if self.env.uid == appr.approver.user_id.id:
    #                 ids.append(exc.id)
    #
    #     # a = re.search("^admin", self.env.user.login)
    #     print('aaaaaaaa')
    #     if self.env.user.has_group('sure_hr_self_service.self_service_group'):
    #         domain = ['|', ('employee_id.user_id', '=', self.env.uid),
    #                   ('id', 'in', ids)]
    #     return {
    #         'name': _("HR Resignation"),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'hr.resignation',
    #         'view_mode': 'tree,form',
    #         # 'view_type': 'form',
    #         'target': 'current',
    #         'domain': domain,
    #     }