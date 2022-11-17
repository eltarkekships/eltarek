# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime, timedelta
import math
from odoo.exceptions import UserError
import re


class OverTime(models.Model):
    _name = 'over.time'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=False, default='Overtime')
    comment = fields.Char(string="Comment", required=True, )
    date_from = fields.Datetime(string="Date From")

    @api.onchange('date_from')
    def onchange_date_from(self):
        if self.date_from:
            self.date_to = self.date_from

    date_to = fields.Datetime(string="Date To")

    @api.constrains('date_from', 'date_to')
    def _check_dates_from_to(self):
        if self.date_from and self.date_to:
            if self.date_to <= self.date_from:
                raise UserError(_('Date To can not be before Or equal Date From.'))

    project_id = fields.Many2one('project.project', required=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, )
    code = fields.Char(string='Code',related='employee_id.old_id',store=True)
    state = fields.Selection(string="", selection=[('draft', 'Draft'), ('approved', 'Approved'), ('done', 'Done')],
                             default='draft')
    company_id = fields.Many2one(comodel_name="res.company")
    holiday_type = fields.Selection([('holiday', 'Holiday'),
                                     ('schedule_day', 'Working Day')])

    amount = fields.Float(compute='_compute_hours')
    morning_hours = fields.Float(compute='_compute_hours', store=True)
    night_hours = fields.Float(compute='_compute_hours', store=True)
    holiday_hours = fields.Float(compute='_compute_hours', store=True)
    total_hours = fields.Float(compute='_compute_hours', store=True)

    @api.depends('employee_id')
    def compute_basic(self):
        for rec in self:
            contract_id = rec.env['hr.contract'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract_id:
                rec.basic = contract_id.wage
            else:
                rec.basic = 0

    basic = fields.Float(compute='compute_basic', store=True)


    attendance_id = fields.Many2one('hr.attendance')
    payslip_id = fields.Many2one('hr.payslip')

    def _get_morning_night_hours(self, date_from, date_to, morning_start_hour):
        # TODO: Refactor and clean the code.
        day_zero_str = "1970-01-01 %s:00:00" % morning_start_hour
        day_zero = datetime.strptime(day_zero_str, '%Y-%m-%d %H:%M:%S')

        time_diff = (date_to - date_from).total_seconds() / 86400 * 2

        mapped_from = (date_from - day_zero).total_seconds() / 86400 * 2
        mapped_to = (date_to - day_zero).total_seconds() / 86400 * 2

        from_ceil = math.ceil(mapped_from)
        from_floor = math.floor(mapped_from)
        to_floor = math.floor(mapped_to)

        morning = 0
        night = 0

        start_morning = False
        end_morning = False

        if from_floor % 2 == 0:  # even
            start_morning = True

        if to_floor % 2 == 0:  # even
            end_morning = True

        if from_floor == to_floor:
            if start_morning:  # morning
                morning = time_diff
            else:
                night = time_diff
        else:
            if start_morning:
                morning += (from_ceil - mapped_from)
            else:
                night += (from_ceil - mapped_from)

            time_diff -= (from_ceil - mapped_from)

            if end_morning:
                morning += (mapped_to - to_floor)
            else:
                night += (mapped_to - to_floor)

            time_diff -= (mapped_to - to_floor)

            if time_diff:
                diff = to_floor - from_ceil
                if diff >= 2:
                    morning += ((diff - (diff % 2)) / 2)
                    night += ((diff - (diff % 2)) / 2)
                    diff = diff % 2

                if diff:
                    if from_ceil % 2 == 0 and to_floor % 2 != 0:
                        morning += diff
                    elif from_ceil % 2 != 0 and to_floor % 2 == 0:
                        night += diff

        return {
            'morning_hours': (morning * 24) / 2,
            'night_hours': (night * 24) / 2
        }

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_hours(self):
        for rec in self:
            rec = rec.sudo()
            if rec.date_from and rec.date_to:
                employee = rec.employee_id
                date_from_date = datetime.strptime(str(rec.date_from), '%Y-%m-%d %H:%M:%S').date()
                date_from_day = str((int(datetime.strftime(date_from_date, '%w')) - 1) % 7)
                schedule_days = [it.dayofweek for it in employee.resource_calendar_id.attendance_ids]
                lines = rec.env['hr.holidays.public.line'].search([])
                if date_from_day not in schedule_days or date_from_date in lines.mapped('date'):
                    rec.holiday_type = 'holiday'
                else:
                    rec.holiday_type = 'schedule_day'

                if rec.holiday_type == 'holiday':
                    rec.morning_hours = rec.night_hours = 0
                    rec.holiday_hours = (rec.date_to - rec.date_from).total_seconds() / 3600

                else:
                    morning_start_hour = str(
                        rec.env['ir.config_parameter'].sudo().get_param('morning_start_hour', default=5)) or "05"
                    # TODO: resolve hardcoded time zone +2.
                    date_from = datetime.strptime(str(rec.date_from), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)
                    date_to = datetime.strptime(str(rec.date_to), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)

                    morning_night_hours = rec._get_morning_night_hours(date_from, date_to, morning_start_hour)

                    rec.morning_hours = morning_night_hours['morning_hours']
                    rec.night_hours = morning_night_hours['night_hours']
                    rec.holiday_hours = 0

                # rec.total_hours = rec.morning_hours + rec.night_hours + rec.holiday_hours
                contract_id = rec.env['hr.contract'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
                try:
                    days_per_month = contract_id.__getattribute__('num_working_days_month')
                except:
                    days_per_month = 30

                try:
                    hours_per_day = contract_id.__getattribute__('num_working_hours_day')
                except:
                    hours_per_day = 8
                if contract_id:
                    employee_rate = contract_id.wage / (days_per_month * hours_per_day)
                else:
                    employee_rate = 0
                overtime_morning_rate = float(
                    rec.env['ir.config_parameter'].sudo().get_param('daily_rate', default=1)) or 1
                overtime_night_rate = float(
                    rec.env['ir.config_parameter'].sudo().get_param('night_rate', default=1)) or 1
                overtime_holiday_rate = float(
                    rec.env['ir.config_parameter'].sudo().get_param('holiday_rate', default=1)) or 1
                rec.amount = employee_rate * (
                            (rec.morning_hours * overtime_morning_rate) + (rec.night_hours * overtime_night_rate) + (
                            rec.holiday_hours * overtime_holiday_rate))
                rec.total_hours = (rec.morning_hours * overtime_morning_rate) + (rec.night_hours * overtime_night_rate) + (
                            rec.holiday_hours * overtime_holiday_rate)
            else:
                rec.amount = 0

    def migrate_company(self):
        records = self.search([])
        for p in records:
            p.company_id = p.employee_id.company_id.id

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.update({
            'company_id': self.employee_id.company_id.id
        })

    @api.model
    def create(self, vals):
        # vals['name'] = self.env['ir.sequence'].next_by_code('over.time')
        if 'employee_id' in vals:
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            vals['company_id'] = employee.company_id.id
        return super(OverTime, self).create(vals)

    def action_done(self):
        for rec in self:
            rec.write({'state': 'done'})

    def action_approve(self):
        for rec in self:
            rec.write({'state': 'approved'})

    def filter(self):
        domain = []
        employees = self.env['hr.employee'].search([])
        overtimes = self.env['over.time'].search([('employee_id', 'in', employees.ids)])
        ids = []
        for exc in overtimes:
            for appr in exc.sudo().employee_id.holidays_approvers:
                if self.env.uid == appr.approver.user_id.id:
                    ids.append(exc.id)

        # a = re.search("^admin", self.env.user.login)
        # print('aaaaaaaa')
        if self.env.user.has_group('sure_hr_self_service.self_service_group'):
            domain = ['|', ('employee_id.user_id', '=', self.env.uid),
                      ('id', 'in', ids)]
        if re.search("^admin", self.env.user.login):
            domain = []
        return {
            'name': _("Over Time"),
            'type': 'ir.actions.act_window',
            'res_model': 'over.time',
            'view_mode': 'tree,form',
            # 'view_type': 'form',
            'target': 'current',
            'domain': domain,
        }
