from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError, AccessError


class HrMission(models.Model):
    _name = 'hr.mission'
    # _inherit = 'hr.self.service'
    _inherit = ['hr.self.service', 'mail.thread', 'mail.activity.mixin']

    start_date = fields.Datetime()
    end_date = fields.Datetime()
    period = fields.Float(compute='_compute_period')
    name = fields.Char(default='Mission')

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
                rec.period = (rec.end_date - rec.start_date).total_seconds() / 3600.0

    def validate(self):
        super(HrMission, self).validate()
        self.env['resource.calendar.leaves'].create({
            'name': 'HR Mission: %s' % (self.comment if self.comment else ''),
            'resource_id': self.employee_id.resource_id.id,
            'calendar_id': self.employee_id.resource_calendar_id.id,
            'date_from': self.start_date,
            'date_to': self.end_date
        })



