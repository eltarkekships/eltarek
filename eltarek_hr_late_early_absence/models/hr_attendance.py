from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.addons.resource.models.resource import float_to_time


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    late_attendance_hours = fields.Float()
    early_leave_hours = fields.Float()

    def time_to_float(self, time):
        return time.hour + time.minute / 60.0

    @api.constrains('check_in')
    def _compute_late_hours(self):
        if self.check_in:
            employee = self.employee_id
            if employee.id == 811:
                print('SSAS')
            # TODO: fix hard coded Timezone +2 "timedelta(hours=2)"
            check_in_datetime = datetime.strptime(str(self.check_in), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)
            check_in_date = check_in_datetime.date()
            check_in_day = str((int(datetime.strftime(check_in_date, '%w')) - 1) % 7)
            schedule_days = [it for it in employee.resource_calendar_id.attendance_ids]
            resource_calendar = employee.resource_calendar_id

            for it in schedule_days:
                if it.dayofweek == check_in_day:
                    if resource_calendar.schedule_type == 'fixed':
                        diff = self.time_to_float(check_in_datetime.time()) - it.hour_from
                        if diff > 0:
                            emp_start = datetime.combine(check_in_date, float_to_time(it.hour_from)) - timedelta(
                                hours=2)
                            domain_me1 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('start_date', '<=', check_in_datetime), ('start_date', '>=', emp_start),
                                          ('end_date', '<=', check_in_datetime), ('end_date', '>=', emp_start)]
                            domain_me2 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('start_date', '<=', check_in_datetime),
                                          ('start_date', '>=', emp_start),
                                          ('end_date', '>', check_in_datetime)]
                            domain_me3 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('start_date', '<', emp_start),
                                          ('end_date', '>=', emp_start),
                                          ('end_date', '<=', check_in_datetime)]

                            domain1 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                       ('date_from', '<=', check_in_datetime), ('date_from', '>=', emp_start),
                                       ('date_to', '<=', check_in_datetime), ('date_to', '>=', emp_start)]
                            domain2 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                       ('date_from', '<=', check_in_datetime),
                                       ('date_from', '>=', emp_start),
                                       ('date_to', '>', check_in_datetime)]
                            domain3 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                       ('date_from', '<', emp_start),
                                       ('date_to', '>=', emp_start),
                                       ('date_to', '<=', check_in_datetime)]
                            mission = sum(self.env['hr.mission'].search(domain_me1).mapped('period'))
                            mission += sum([(check_in_datetime - line.start_date).total_seconds() / 3600 for line in
                                            self.env['hr.mission'].search(domain_me2)])
                            mission += sum([(line.end_date - emp_start).total_seconds() / 3600 for line in
                                            self.env['hr.mission'].search(domain_me3)])

                            excuse = sum(self.env['hr.excuse'].search(domain_me1).mapped('period'))
                            excuse += sum([(check_in_datetime - line.start_date).total_seconds() / 3600 for line in
                                           self.env['hr.excuse'].search(domain_me2)])
                            excuse += sum([(line.end_date - emp_start).total_seconds() / 3600 for line in
                                           self.env['hr.excuse'].search(domain_me3)])
                            leave = sum(self.env['hr.leave'].search(domain1).mapped('number_of_days'))
                            leave += sum([(check_in_datetime - line.date_from).total_seconds() / 3600 for line in
                                          self.env['hr.leave'].search(domain2)])
                            leave += sum([(line.date_to - emp_start).total_seconds() / 3600 for line in
                                          self.env['hr.leave'].search(domain3)])
                            result = mission + excuse + leave
                            diff = diff - result
                        self.late_attendance_hours = diff if diff > 0 else 0
                    elif resource_calendar.schedule_type == 'flexible':
                        diff = self.time_to_float(check_in_datetime.time()) - it.hour_from_flexible
                        if diff > 0:
                            emp_start = datetime.combine(check_in_date,
                                                         float_to_time(it.hour_from_flexible)) - timedelta(
                                hours=2)
                            domain_me1 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('start_date', '<=', check_in_datetime), ('start_date', '>=', emp_start),
                                          ('end_date', '<=', check_in_datetime), ('end_date', '>=', emp_start)]
                            domain_me2 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('start_date', '<=', check_in_datetime),
                                          ('start_date', '>=', emp_start),
                                          ('end_date', '>', check_in_datetime)]
                            domain_me3 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('start_date', '<', emp_start),
                                          ('end_date', '>=', emp_start),
                                          ('end_date', '<=', check_in_datetime)]

                            domain1 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                       ('date_from', '<=', check_in_datetime), ('date_from', '>=', emp_start),
                                       ('date_to', '<=', check_in_datetime), ('date_to', '>=', emp_start)]
                            domain2 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                       ('date_from', '<=', check_in_datetime),
                                       ('date_from', '>=', emp_start),
                                       ('date_to', '>', check_in_datetime)]
                            domain3 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                       ('date_from', '<', emp_start),
                                       ('date_to', '>=', emp_start),
                                       ('date_to', '<=', check_in_datetime)]
                            mission = sum(self.env['hr.mission'].search(domain_me1).mapped('period'))
                            mission += sum([(check_in_datetime - line.start_date).total_seconds() / 3600 for line in
                                            self.env['hr.mission'].search(domain_me2)])
                            mission += sum([(line.end_date - emp_start).total_seconds() / 3600 for line in
                                            self.env['hr.mission'].search(domain_me3)])

                            excuse = sum(self.env['hr.excuse'].search(domain_me1).mapped('period'))
                            excuse += sum([(check_in_datetime - line.start_date).total_seconds() / 3600 for line in
                                           self.env['hr.excuse'].search(domain_me2)])
                            excuse += sum([(line.end_date - emp_start).total_seconds() / 3600 for line in
                                           self.env['hr.excuse'].search(domain_me3)])
                            leave = sum(self.env['hr.leave'].search(domain1).mapped('number_of_days'))
                            leave += sum([(check_in_datetime - line.date_from).total_seconds() / 3600 for line in
                                          self.env['hr.leave'].search(domain2)])
                            leave += sum([(line.date_to - emp_start).total_seconds() / 3600 for line in
                                          self.env['hr.leave'].search(domain3)])
                            result = mission + excuse + leave
                            diff = diff - result
                        self.late_attendance_hours = diff if diff > 0 else 0
                    elif resource_calendar.schedule_type == 'open':
                        pass

                    break

    @api.constrains('check_in', 'check_out')
    def _compute_early_hours(self):
        if self.check_in and self.check_out:
            employee = self.employee_id

            # TODO: fix hard coded Timezone +2 "timedelta(hours=2)"
            check_in_datetime = datetime.strptime(str(self.check_in), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)
            check_out_datetime = datetime.strptime(str(self.check_out), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)

            check_in_date = check_in_datetime.date()
            check_out_date = check_out_datetime.date()
            check_in_day = str((int(datetime.strftime(check_in_date, '%w')) - 1) % 7)
            schedule_days = [it for it in employee.resource_calendar_id.attendance_ids]
            resource_calendar = employee.resource_calendar_id

            for it in schedule_days:
                if it.dayofweek == check_in_day:
                    if resource_calendar.schedule_type == 'fixed':
                        diff = it.hour_to - self.time_to_float(check_out_datetime.time())
                        if diff > 0:
                            emp_end = datetime.combine(check_out_date, float_to_time(it.hour_to)) - timedelta(
                                hours=2)
                            domain_me1 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('end_date', '>=', check_out_datetime), ('end_date', '<=', emp_end),
                                          ('start_date', '>=', check_out_datetime), ('start_date', '<=', emp_end)]
                            domain_me2 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('end_date', '>=', check_out_datetime), ('end_date', '<=', emp_end),
                                          ('start_date', '<', check_out_datetime)]
                            domain_me3 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('end_date', '>', emp_end),
                                          ('start_date', '>=', check_out_datetime), ('start_date', '<=', emp_end)]
                            domain1 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('date_to', '>=', check_out_datetime), ('date_to', '<=', emp_end),
                                          ('date_from', '>=', check_out_datetime), ('date_from', '<=', emp_end)]
                            domain2 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('date_to', '>=', check_out_datetime), ('date_to', '<=', emp_end),
                                          ('date_from', '<', check_out_datetime)]
                            domain3 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('date_to', '>', emp_end),
                                          ('date_from', '>=', check_out_datetime), ('date_from', '<=', emp_end)]
                            mission = sum(self.env['hr.mission'].search(domain_me1).mapped('period'))
                            mission += sum([(line.end_date - check_out_datetime).total_seconds() / 3600 for line in
                                            self.env['hr.mission'].search(domain_me2)])
                            mission += sum([(emp_end - line.start_date).total_seconds() / 3600 for line in
                                            self.env['hr.mission'].search(domain_me3)])

                            excuse = sum(self.env['hr.excuse'].search(domain_me1).mapped('period'))
                            excuse += sum([(line.end_date - check_out_datetime).total_seconds() / 3600 for line in
                                           self.env['hr.excuse'].search(domain_me2)])
                            excuse += sum([(emp_end - line.start_date).total_seconds() / 3600 for line in
                                           self.env['hr.excuse'].search(domain_me3)])
                            leave = sum(self.env['hr.leave'].search(domain1).mapped('number_of_days'))
                            leave += sum([(line.date_to - check_out_datetime).total_seconds() / 3600 for line in
                                          self.env['hr.leave'].search(domain2)])
                            leave += sum([(emp_end - line.date_from).total_seconds() / 3600 for line in
                                          self.env['hr.leave'].search(domain3)])
                            result = mission + excuse + leave
                            diff = diff - result
                        self.early_leave_hours = diff if diff > 0 else 0
                    elif resource_calendar.schedule_type == 'flexible':
                        working_hours = it.hour_to - it.hour_from
                        hour_to_flexible = it.hour_to_flexible if it.hour_to_flexible >= it.hour_to else it.hour_to_flexible + 24.0
                        check_in_float = self.time_to_float(check_in_datetime.time())
                        check_out_float = self.time_to_float(check_out_datetime.time())
                        check_out_reference = min(hour_to_flexible, check_in_float + working_hours)

                        if check_out_float < check_in_float:
                            check_out_float += 24

                        diff = check_out_reference - check_out_float
                        if diff > 0:
                            emp_end = datetime.combine(check_out_date, float_to_time(it.hour_to_flexible)) - timedelta(
                                hours=2)
                            domain_me1 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('end_date', '>=', check_out_datetime), ('end_date', '<=', emp_end),
                                          ('start_date', '>=', check_out_datetime), ('start_date', '<=', emp_end)]
                            domain_me2 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('end_date', '>=', check_out_datetime), ('end_date', '<=', emp_end),
                                          ('start_date', '<', check_out_datetime)]
                            domain_me3 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                          ('end_date', '>', emp_end),
                                          ('start_date', '>=', check_out_datetime), ('start_date', '<=', emp_end)]
                            domain1 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                       ('date_to', '>=', check_out_datetime), ('date_to', '<=', emp_end),
                                       ('date_from', '>=', check_out_datetime), ('date_from', '<=', emp_end)]
                            domain2 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                       ('date_to', '>=', check_out_datetime), ('date_to', '<=', emp_end),
                                       ('date_from', '<', check_out_datetime)]
                            domain3 = [('employee_id', '=', employee.id), ('state', '=', 'validate'),
                                       ('date_to', '>', emp_end),
                                       ('date_from', '>=', check_out_datetime), ('date_from', '<=', emp_end)]
                            mission = sum(self.env['hr.mission'].search(domain_me1).mapped('period'))
                            mission += sum([(line.end_date - check_out_datetime).total_seconds() / 3600 for line in
                                            self.env['hr.mission'].search(domain_me2)])
                            mission += sum([(emp_end - line.start_date).total_seconds() / 3600 for line in
                                            self.env['hr.mission'].search(domain_me3)])

                            excuse = sum(self.env['hr.excuse'].search(domain_me1).mapped('period'))
                            excuse += sum([(line.end_date - check_out_datetime).total_seconds() / 3600 for line in
                                           self.env['hr.excuse'].search(domain_me2)])
                            excuse += sum([(emp_end - line.start_date).total_seconds() / 3600 for line in
                                           self.env['hr.excuse'].search(domain_me3)])
                            leave = sum(self.env['hr.leave'].search(domain1).mapped('number_of_days'))
                            leave += sum([(line.date_to - check_out_datetime).total_seconds() / 3600 for line in
                                          self.env['hr.leave'].search(domain2)])
                            leave += sum([(emp_end - line.date_from).total_seconds() / 3600 for line in
                                          self.env['hr.leave'].search(domain3)])
                            result = mission + excuse + leave
                            diff = diff - result
                        self.early_leave_hours = diff if diff > 0 else 0
                    elif resource_calendar.schedule_type == 'open':
                        pass

                    break
        else:
            self.early_leave_hours = 0

    def is_absent(self, employee, date):
        date_dayofweek = str((int(datetime.strftime(date, '%w')) - 1) % 7)
        resource_calendar = employee.resource_calendar_id
        schedule_days = [it.dayofweek for it in resource_calendar.attendance_ids] if resource_calendar else []
        if date_dayofweek not in schedule_days:
            return False

        attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id)])
        for att in attendance:
            if datetime.strptime(str(att.local_check_in), '%Y-%m-%d %H:%M:%S').date() == date:
                return False

        leaves = self.env['resource.calendar.leaves'].search([('holiday_id.employee_id.id', '=', employee.id)])
        for leave in leaves:
            if leave.date_from.date() <= date <= leave.date_to.date():
                # stopped condition,so any leave,mission,excuse that in this day
                # regardless start,end date of request, if request is found means employee not absent
                # if (leave.date_to - leave.date_from).total_seconds() / 3600.0 >= 24:
                return False

        ##check day is in public holidays,then not absent
        public_dates = []
        puplic_holidays = self.env['hr.holidays.public.line'].search([])
        for rec in puplic_holidays:
            public_dates.append(str(rec.date))
        print("public_dates", public_dates)
        if str(date) in public_dates:
            return False

        #
        return True

    @api.model
    def _update_absence(self, date=datetime.now().date()):
        # for day_before_ in range(1, 44):#temporary
        previous_date = date - timedelta(days=1)  # day_before_
        employees = self.env['hr.employee'].search([])
        for emp in employees:
            if self.is_absent(emp, previous_date):
                self.env['hr.absence'].create({'employee_id': emp.id, 'date': previous_date})
