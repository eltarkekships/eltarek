from odoo import models, fields, api, _
import re

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def action_makeMeeting(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        self = self.sudo()
        self.ensure_one()
        partners = self.partner_id | self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id

        category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window']._for_xml_id('calendar.action_calendar_event')
        res['context'] = {
            'default_partner_ids': partners.ids,
            'default_user_id': self.env.uid,
            'default_name': self.name,
            'default_categ_ids': category and [category.id] or False,
        }
        return res

    hiring_request_id = fields.Many2one('hr.hiring.request')

class HrHiringRequest(models.Model):
    _name = 'hr.hiring.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee')
    job_id = fields.Many2one('hr.job')
    department_id = fields.Many2one('hr.department', related='job_id.department_id')
    date = fields.Date()
    number_of_vacancies = fields.Integer()
    educational_degree = fields.Char()
    years_of_experience = fields.Integer()
    salary = fields.Float()
    require_travel = fields.Boolean()
    job_requirements = fields.Text()
    state = fields.Selection(string="State",
                             selection=[('open', 'Open'), ('cancel', 'Canceled'), ('done', 'Done')],
                             default='open',
                             required=False)
    type = fields.Selection([('replace', 'Replace Employee'), ('addition', 'Addition to current staff')])
    application_ids = fields.One2many('hr.applicant', 'hiring_request_id')

    def filter(self):
        domain = []
        employees = self.env['hr.employee'].search([])
        hirings = self.env['hr.hiring.request'].search([('employee_id','in',employees.ids)])
        ids = []
        for exc in hirings:
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
            'name': _("Hiring Request"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hiring.request',
            'view_mode': 'tree,form',
            # 'view_type': 'form',
            'target': 'current',
            'domain': domain,
        }


    # @api.multi
    def open(self):
        for rec in self:
            rec.state = 'open'

    # @api.multi
    def done(self):
        for rec in self:
            rec.state = 'done'

    # @api.multi
    def cancel(self):
        for rec in self:
            rec.state = 'cancel'


    @api.model
    def create(self, vals):
        res = super(HrHiringRequest, self).create(vals)
        # res.employee_id = self.env.user.employee_ids[0] if self.env.user.employee_ids else False
        return res

    # @api.one
    @api.depends('job_id')
    def _compute_name(self):
        self.name = self.job_id.name
