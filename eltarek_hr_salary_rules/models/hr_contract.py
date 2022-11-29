# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import ValidationError
from datetime import date
from dateutil import relativedelta
from odoo.http import request
import logging
import calendar
from datetime import timedelta


LOGGER = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'


    def get_work_ratio(self,date_from,date_to):

        salary_start = max(self.date_start,date_from)
        salary_end = min(self.date_end,date_to) if self.date_end else date_to

        # This the case of normal payslip (month does not contain join date or contract end )
        if salary_start == date_from and salary_end == date_to:
            return 1

        salary_start_datetime = fields.Datetime.from_string(salary_start)
        salary_end_datetime = fields.Datetime.from_string(salary_end)
        month_days_count = 7
        month_end = fields.Datetime.from_string(date_to)
        month_start = fields.Datetime.from_string(date_from)

        payslip_days = (month_end - month_start).days + 1

        # The case of month contain contract end i.e. employee termination or resignation
        if salary_start == date_from:
            num_work_days = (salary_end_datetime - salary_start_datetime).days + 1

        # The case of month contain join date i.e. first month for an employee (new employee)
        elif salary_end == date_to:
            num_work_days = (salary_end_datetime - salary_start_datetime).days + 1


        # The case of employee that join and resigned on the same month
        else:
            num_work_days = (salary_end_datetime - salary_start_datetime).days + 1

        # num_work_days = num_work_days + month_days_count - payslip_days
        print(num_work_days)
        return (1.0 * num_work_days) / (1.0 * month_days_count)



    # def public_time_off_dates(self):
    #     # Return list of datetime.date objects between start_date and end_date inside public time off (inclusive)
    #     for rec in self.resource_calendar_id.global_leave_ids:
    #         date_off = []
    #         start = rec.date_from.replace(hour=0,microsecond=0, second=0, minute=0)
    #         date_form = rec.date_from + timedelta(hours=2)
    #         date_to = rec.date_to + timedelta(hours=2)
    #         # end = rec.date_to.replace(hour=21,microsecond=0, second=0, minute=0)
    #         while start <= date_form <= date_to:
    #             date_off.append(date_form.strftime('%A'))
    #             date_form += timedelta(days=1)
    #         return date_off

    def date_range_list(self,start_date, end_date):
        # Return list of datetime.date objects between start_date and end_date (inclusive).
        date_list = []
        curr_date = start_date
        while curr_date <= end_date:
            date_list.append(curr_date.strftime('%A'))
            curr_date += timedelta(days=1)
        return date_list

    def basic_salary_rule(self,payslip):
        payslip = payslip.dict
        schdule_list = []
        payslip_list = []
        days_list = []
        for work in self.resource_calendar_id.attendance_ids:
            work_day = dict(work._fields['dayofweek'].selection).get(work.dayofweek)
            schdule_list.append(work_day)
        dates = self.date_range_list(payslip.date_from,payslip.date_to)
        # days_off = self.public_time_off_dates()
        schedule = list(set(schdule_list))
        for date in dates:
            if date in schedule:
                payslip_list.append(date)
        # if days_off:
        #     days_list = list(set(payslip_list) - set(days_off))
        # days = len(days_list)
        days = len(payslip_list)
        total = days * self.day_value
        return total


    def travel_allowance_weekly_monthly(self,payslip):
        if payslip.date_from >= self.date_start:
            payslip_dates = abs(payslip.date_from - payslip.date_to).days
            if payslip_dates <= 7:
                total = self.travel_allwoance / 4
            else:
                total = self.travel_allwoance
            return total
        else:
            return 0


    def car_allowance_weekly_monthly(self,payslip):
        if payslip.date_from >= self.date_start:
            payslip_dates = abs(payslip.date_from - payslip.date_to).days
            if payslip_dates <= 7:
                total = self.car_allwoance / 4
            else:
                total = self.car_allwoance
            return total
        else:
            return 0


    def house_allowance_weekly_monthly(self,payslip):
        if payslip.date_from >= self.date_start:
            payslip_dates = abs(payslip.date_from - payslip.date_to).days
            if payslip_dates <= 7:
                total = self.house_allwoance / 4
            else:
                total = self.house_allwoance
            return total
        else:
            return 0

    def other_allowance_weekly_monthly(self,payslip):
        if payslip.date_from >= self.date_start:
            payslip_dates = abs(payslip.date_from - payslip.date_to).days
            if payslip_dates <= 7:
                total = self.other_allwoance / 4
            else:
                total = self.other_allwoance
            return total
        else:
            return 0