# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import datetime
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def overtime_total_hours(self,payslip,contract):
        overtime = self.env['over.time'].search(
            [('employee_id', '=', self.id)])
        total = 0
        if overtime:
            for rec in overtime:
                if payslip.date_from <= rec.date_from.date() <= payslip.date_to:
                    if 1 < rec.total_hours < 5:
                        total += contract.day_value / 2
                    elif rec.total_hours > 5 :
                        total += contract.day_value
            return total


    def mission_employee_value(self, payslip):
        mission = self.env['hr.mission'].search(
            [('employee_id', '=', self.id), ('payslip_checked', '=', False), ('state', '=', 'validate')])
        total = 0
        if mission:
            for rec in mission:
                if payslip.date_from <= rec.start_date.date() <= payslip.date_to:
                    total += rec.value
            return total
