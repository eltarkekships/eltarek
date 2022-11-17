from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError
from dateutil.relativedelta import relativedelta

from datetime import datetime, timedelta
import calendar
import re


class HrExcuse(models.Model):
    _name = 'hr.excuse'
    # _inherit = 'hr.self.service'
    _inherit = ['hr.self.service', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(default='Excuse')

    def filter(self):
        domain = []
        employees = self.env['hr.employee'].search([])
        excuses = self.env['hr.excuse'].search([('employee_id', 'in', employees.ids)])
        ids = []
        for exc in excuses:
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
            'name': _("HR Excuse"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.excuse',
            'view_mode': 'tree,form',
            # 'view_type': 'form',
            'target': 'current',
            'domain': domain,
        }

    # def leave_page(self):  # hr_holidays.menu_hr_holidays_approvals
    #     menu_id = self.env.ref('hr_holidays.menu_hr_holidays_root')
    #     action_id = self.env.ref('sure_hr_holidays_multi_levels_approval.open_holidays_approve')
    #     base_url = request.env['ir.config_parameter'].get_param('web.base.url')
    #     base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
    #     base_url += '&menu_id=%d&action=%d' % (menu_id.id, action_id.id)
    #     return base_url
    #
    # def send_emailto_approv(self, employee_name, approver_email, leave_page_url):
    #     message = """ Leave Request from employee: """ + employee_name + '<br>' + """
    #     <br> You can access leave details from here: <br>""" + leave_page_url
    #
    #     try:
    #         Mail = self.env['mail.mail']
    #         outgoing_mail = self.env['ir.mail_server'].search([], limit=1)
    #         if not outgoing_mail or not outgoing_mail.smtp_port or not outgoing_mail.smtp_user or not outgoing_mail.smtp_pass:
    #             raise UserError(
    #                 _('Outgoing email should be configured well,please contact us!'))
    #
    #         # mail values
    #         mail_values = {
    #             'subject': 'Sure Leave Request',
    #             'author_id': 1,
    #             'email_from': 'Sure' + ' <' + outgoing_mail.smtp_user + '>',
    #             'email_to': approver_email,
    #             'body_html': message,
    #         }
    #
    #         # create mail, that will create it in odoo mails
    #         created_mail = Mail.create(mail_values)
    #
    #         # send mail
    #         created_mail.send()
    #
    #         return "sent"
    #     except Exception as e:
    #         return str(e)
    #
    # def send_notification(self, partner_id, employee_name, leave_page_url):
    #     o = self.env['mail.message'].search([('record_name', '!=', False)],
    #                                         limit=1)
    #     notification_ids = [(0, 0, {
    #         'res_partner_id': partner_id,
    #         'notification_type': 'inbox'
    #     })]
    #     self.message_post(body=""" Leave Request from employee: """ + employee_name + '<br>' + """
    #     # <br> You can access leave details from here: <br>""" + """<a href=%s>%s</a>""" % (
    #     leave_page_url, employee_name), message_type="notification",
    #                       subtype_xmlid="mail.mt_comment",
    #                       author_id=self.env.user.partner_id.id,
    #                       notification_ids=notification_ids)
    #     #
    #     # h = [(0, 0, {'mail_message_id': o.id, 'res_partner_id': partner_id})]
    #     # self.env['mail.message'].sudo().create({
    #     #     'subject': 'Contract End Date',
    #     #     'body': """ Leave Request from employee: """ + employee_name + '<br>' + """
    #     # <br> You can access leave details from here: <br>""" + """<a href=%s>%s</a>""" % (leave_page_url,employee_name),
    #     #     'email_from': self.env.user.name,
    #     #     'notification_ids': h,
    #     #     'partner_ids': [(6, 0, [partner_id])],
    #     #     'message_type': 'notification',
    #     #     'subtype_id': self.env.ref('mail.mt_note').id,
    #     # })
    #
    # def notify_with_email(self):
    #     # send email to approvers
    #     for holiday in self:
    #         if holiday.employee_id.holidays_approvers:
    #             for rec in holiday.employee_id.holidays_approvers:
    #                 approver_email = rec.approver.user_id.email
    #                 approver_partner = rec.approver.user_id.partner_id.id
    #                 self.sudo().send_notification(approver_partner, holiday.employee_id.name, self.sudo().leave_page())
    #                 self.sudo().send_emailto_approv(holiday.employee_id.name, approver_email, self.sudo().leave_page())
    #
    # def notify_approvers(self):
    #     self.sudo().notify_with_email()
    #
    # @api.model
    # def create(self, values):
    #     """ Override to avoid automatic logging of creation """
    #     holiday = super(HrExcuse, self).create(values)
    #     # holiday.sudo().state = 'confirm'
    #     holiday.notify_approvers()
    #     return holiday

    start_date = fields.Datetime()
    end_date = fields.Datetime()
    period = fields.Float(compute='_compute_period', store=True)

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date:
            self.end_date = fields.Datetime.from_string(self.start_date) + timedelta(
                hours=self.employee_id.max_excuse_period)

    @api.constrains('period', 'start_date', 'employee_id', 'end_date', 'state')
    def _check_period(self):
        max_period = self.employee_id.max_excuse_period
        if self.period > max_period:
            raise UserError(_('Period exceeds employee\'s allowed period.'))
        month = self.start_date.month
        year = self.start_date.year
        day = self.start_date.day
        month_start = datetime(day=1, month=month, year=year, hour=0, minute=0, second=0)
        month_end = datetime(day=calendar.monthrange(year, month)[1], month=month, year=year, hour=23, minute=59,
                             second=59)
        # month_start = (self.start_date - relativedelta(months=1)).replace(day=16, hour=0, minute=0,
        #                                                                   second=0) if day < 16 else datetime(day=16,
        #                                                                                                       month=month,
        #                                                                                                       year=year,
        #                                                                                                       hour=0,
        #                                                                                                       minute=0,
        #                                                                                                       second=0)
        # month_end = datetime(day=15, month=month, year=year, hour=23, minute=59, second=59) if day < 16 else (
        #         self.start_date + relativedelta(months=1)).replace(day=15, hour=23, minute=59, second=59)
        max_month_request = self.employee_id.number_excuse_per_month
        excuses_this_month = self.env['hr.excuse'].search([('employee_id', '=', self.employee_id.id),
                                                           ('start_date', '>=', month_start),
                                                           ('end_date', '<=', month_end),
                                                           ('state', '!=', 'refuse')])
        if len(excuses_this_month) > max_month_request:
            raise UserError(_('Period exceeds employee\'s allowed requests per month.'))

    @api.depends('start_date', 'end_date')
    def _compute_period(self):
        if self.end_date and self.start_date:
            self.period = (self.end_date - self.start_date).total_seconds() / 3600.0

    def validate(self):
        super(HrExcuse, self).validate()
        self.env['resource.calendar.leaves'].create({
            'name': 'HR Excuse: %s' % (self.comment if self.comment else ''),
            'resource_id': self.employee_id.resource_id.id,
            'calendar_id': self.employee_id.resource_calendar_id.id,
            'date_from': self.start_date,
            'date_to': self.end_date
        })
