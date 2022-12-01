# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import datetime
from datetime import datetime
from datetime import timedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def date_range_list(self,start_date, end_date):
        # Return list of datetime.date objects between start_date and end_date (inclusive).
        date_list = []
        curr_date = start_date
        while curr_date <= end_date:
            date_list.append(curr_date.strftime('%A'))
            curr_date += timedelta(days=1)
        return date_list


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
        else:
            return 0

    def mission_extra_employee_value(self,payslip,contract):
        schdule_list = []
        date_diff = []
        for work in contract.resource_calendar_id.attendance_ids:
            work_day = dict(work._fields['dayofweek'].selection).get(work.dayofweek)
            schdule_list.append(work_day)
        schedule = list(set(schdule_list))
        mission = self.env['hr.mission'].search(
            [('employee_id', '=', self.id), ('payslip_checked', '=', False), ('state', '=', 'validate')])
        total = 0
        if mission:
            for mis in mission:
                if payslip.date_from <= mis.start_date.date() <= payslip.date_to:
                    dates = self.date_range_list(mis.start_date.date(), mis.end_date.date())
                    for date in dates:
                        if date in schedule:
                            date_diff.append(date)
                    total += len(date_diff) * mis.value
            return total
        else:
            return 0




    def mission_employee_value(self, payslip):
        mission = self.env['hr.mission'].search(
            [('employee_id', '=', self.id), ('payslip_checked', '=', False), ('state', '=', 'validate')])
        total = 0
        if mission:
            for rec in mission:
                if payslip.date_from <= rec.start_date.date() + timedelta(days=1) <= payslip.date_to:
                    total += rec.value
            return total
        else:
            return 0
