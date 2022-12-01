from odoo import models, fields, api, _
import re
from datetime import timedelta
from odoo.exceptions import ValidationError, AccessError
from dateutil.relativedelta import relativedelta

class HrMission(models.Model):
    _name = 'hr.mission'
    # _inherit = 'hr.self.service'
    _inherit = ['hr.self.service', 'mail.thread', 'mail.activity.mixin']



    start_date = fields.Datetime()
    end_date = fields.Datetime()
    period = fields.Float(compute='_compute_period')
    name = fields.Char(default='Mission')
    mission_id = fields.Many2one('mission.config')
    value = fields.Float('Value')
    payslip_checked = fields.Boolean('Payslip Checked',compute='compute_payslip_checked')

    def compute_payslip_checked(self):
        mission = self.env['hr.mission'].search([])
        payslip = self.env['hr.payslip'].search([],order='create_date desc',limit=1)
        if mission:
            for rec in mission:
                if payslip:
                    for pay in payslip.line_ids:
                        if pay.code == 'MVSR':
                            rec.payslip_checked = True
                            break
                        else:
                            rec.payslip_checked = False
                else:
                    rec.payslip_checked = False
        else:
            self.payslip_checked = False


        # if payslip:
        #     for rec in mission:
        #         total_pay = rec.value
        #         for line in payslip.line_ids:
        #             if line.code == 'MVSR':
        #                 if line.amount == total_pay:
        #                     rec.payslip_checked = True
        #                 else:
        #                     rec.payslip_checked = False
        #                 break
        # else:
        #     self.payslip_checked = False





    @api.onchange('mission_id')
    def onchange_value(self):
        if self.mission_id:
            if self.employee_id.is_manager == True:
                self.value = self.mission_id.manager_value
            else:
                self.value = self.mission_id.emp_value


    @api.onchange('start_date')
    def onchange_start(self):
        if  self.start_date:
            start_hour = self.start_date.replace(hour=22, second=0, minute=0) + timedelta(days=-1)
            self.start_date = start_hour


    @api.onchange('end_date')
    def onchange_end(self):
        if  self.end_date:
            end_hour = self.end_date.replace(hour=21,microsecond=59, second=59, minute=59)
            self.end_date = end_hour

    def filter(self):
        domain = []
        employees = self.env['hr.employee'].search([])
        missions = self.env['hr.mission'].search([('employee_id','in',employees.ids)])
        ids = []
        for exc in missions:
            for appr in exc.sudo().employee_id.holidays_approvers:
                if self.env.uid == appr.approver.user_id.id:
                    ids.append(exc.id)

        # a = re.search("^admin", self.env.user.login)
        print('aaaaaaaa')
        if self.env.user.has_group('sure_hr_self_service.self_service_group'):
            domain = ['|', ('employee_id.user_id', '=', self.env.uid),
                      ('id', 'in', ids)]
            
        if re.search("^admin", self.env.user.login):
            domain = []
        return {
            'name': _("HR Mission"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.mission',
            'view_mode': 'tree,form',
            # 'view_type': 'form',
            'target': 'current',
            'domain': domain,
        }

    @api.depends('start_date', 'end_date')
    def _compute_period(self):
        for rec in self:
            rec.period = 0
            if rec.end_date and rec.start_date:
                if rec.employee_id.is_manager == True:
                    days = (rec.end_date - rec.start_date).days
                    manager_mission = (days - 2) * 1
                    rec.period = manager_mission + 2
                else:
                    days = (rec.end_date - rec.start_date).days
                    worker_mission = (days - 2) * 0.5
                    rec.period = worker_mission + 2

    def validate(self):
        super(HrMission, self).validate()
        self.env['resource.calendar.leaves'].create({
            'name': 'HR Mission: %s' % (self.comment if self.comment else ''),
            'resource_id': self.employee_id.resource_id.id,
            'calendar_id': self.employee_id.resource_calendar_id.id,
            'date_from': self.start_date,
            'date_to': self.end_date
        })



