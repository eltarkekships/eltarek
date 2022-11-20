# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo.http import request


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hr_code = fields.Char('Hr Code')
    arabic_name = fields.Char('Arabic Name')
    hire_date = fields.Date('Hire Date')
    end_probation_period = fields.Date('End Probation Period')
    social_number = fields.Char('Social Insurance Number')
    social_date = fields.Date('Social Insurance Date')
    social_office = fields.Char('Social Insurance Office')
    social_code = fields.Char('Social Insurance Code')
    five_precent = fields.Boolean('5%')
    social_exemption = fields.Boolean('Social Insurance Exemption')
    place_of_issue = fields.Char('Place Of Issue')
    date_of_issue = fields.Date('Date Of Issue')
    expiary_date = fields.Date('Expiary Date')
    payment_method = fields.Selection([('cash','Cash'),('bank','Bank')])
    prepaid = fields.Char('Prepaid')
    bank_account_no = fields.Char('Bank Account Number')
    branch_id = fields.Char('Branch ID')
    bank_name = fields.Char('Bank Name')
    age = fields.Integer('Age',compute='compute_employee_age')
    social_company_id = fields.Many2one('social.insurance.config','Social Company')
    is_driver_rel = fields.Boolean(related='job_id.is_driver')
    driver_job_id = fields.Many2one('driver.line')
    driver_type_job_id = fields.Many2one('driver.type.line','Truck Number')
    old_id = fields.Char(string='Code', default='0')
    is_manager = fields.Boolean('Management')

    @api.constrains('driver_type_job_id')
    def constrains_truck_number(self):
        truck = self.env['hr.employee'].search([('id','!=',self.id)])
        for rec in truck:
            if rec.driver_type_job_id.id == self.driver_type_job_id.id:
                raise ValidationError('Truck Number Must Be Unique')


    @api.onchange('driver_job_id')
    def onchange_domain_driver_job(self):
            return {'domain': {'driver_type_job_id': [('driver_type_id', '=', self.driver_job_id.id)]}}

    @api.depends('birthday')
    def compute_employee_age(self):
        for rec in self:
            if rec.birthday:
                today = date.today()
                age = today.year - rec.birthday.year - ((today.month, today.day) < (rec.birthday.month, rec.birthday.day))
                if age < 0 :
                    raise ValidationError('Age Cannot Be Negative')
                else:
                    rec.age = age
            else:
                rec.age = 0

    @api.constrains('hr_code')
    def unique_hr_code(self):
        hr_code = self.env['hr.employee'].search([('id', '!=', self.id)])
        if hr_code:
            for hr in hr_code:
                if self.hr_code == hr.hr_code:
                    raise ValidationError('HR Code Cannot Be Duplicated')

    def expiary_date_monthly_notify(self):
        employees = self.sudo().search([('active', '=', True)])
        users = self.env['res.users'].search([])
        for employee in employees:
            if employee.expiary_date:
                delta = relativedelta.relativedelta(date.today(), employee.expiary_date)
                if 0 <= delta.months < 1:
                    for user in users:
                        notification_ids = [(0, 0, {
                            'res_partner_id': user.partner_id.id,
                            'notification_type': 'inbox'
                        })]
                        action_id = self.env.ref('hr.open_view_employee_list_my')  # action id
                        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        base_url += '/web#id=%d&amp;view_type=form&amp' % (employee.id)
                        base_url += '&amp;action=%d' % (action_id.id)
                        employee.message_post(record_name='ID Expiary Date',
                                              body=""" ID Will End In """ + str(abs(delta.months)) + ' ' + 'Months and ' + ' ' + str(abs(delta.days)) + ' ' + 'Days '
                                                   """<br> You can access employee details from here: <br>"""
                                                   + """<a href="%s">Link</a>""" % (
                                                       base_url)
                                              , message_type="notification",
                                              subtype_xmlid="mail.mt_comment",
                                              author_id=user.partner_id.id,
                                              notification_ids=notification_ids,
                                              )

    def employee_end_probation_period_monthly_notify(self):
        employees = self.sudo().search([('active', '=', True)])
        users = self.env['res.users'].search([])
        for employee in employees:
            if employee.end_probation_period:
                delta = relativedelta.relativedelta(date.today(), employee.end_probation_period)
                if delta.months == 3:
                    for user in users:
                        notification_ids = [(0, 0, {
                            'res_partner_id': user.partner_id.id,
                            'notification_type': 'inbox'
                        })]
                        action_id = self.env.ref('hr.open_view_employee_list_my')  # action id
                        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        base_url += '/web#id=%d&amp;view_type=form&amp' % (employee.id)
                        base_url += '&amp;action=%d' % (action_id.id)
                        employee.message_post(record_name='Employee End Probation Period',
                                              body=str(abs(delta.months)) + ' ' + 'Months' + ' ' + """Probation Period Have Passed on """ + employee.name + """ Works As """ + employee.job_title + """ In Department """ + employee.department_id.name +
                                                   """<br> You can access employee details from here: <br>"""
                                                   + """<a href="%s">Link</a>""" % (
                                                       base_url)
                                              , message_type="notification",
                                              subtype_xmlid="mail.mt_comment",
                                              author_id=user.partner_id.id,
                                              notification_ids=notification_ids,
                                              )

    def employee_hire_date_monthly_notify(self):
        employees = self.sudo().search([('active', '=', True)])
        users = self.env['res.users'].search([])
        for employee in employees:
            if employee.hire_date:
                delta = relativedelta.relativedelta(date.today(), employee.hire_date)
                if delta.months == 6:
                    for user in users:
                        notification_ids = [(0, 0, {
                            'res_partner_id': user.partner_id.id,
                            'notification_type': 'inbox'
                        })]
                        action_id = self.env.ref('hr_contract.action_hr_contract')  # action id
                        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        base_url += '/web#id=%d&amp;view_type=form&amp' % (employee.contract_id.id)
                        base_url += '&amp;action=%d' % (action_id.id)
                        employee.message_post(record_name='Contract Hire Date',
                                              body=str(abs(delta.months)) + ' ' + 'Months' + ' ' + """Have Passed on Contract Since Hire For """ + employee.name + """ Works As """ + employee.job_title + """ In Department """ + employee.department_id.name +
                                                   """<br> You can access contract details from here: <br>"""
                                                   + """<a href="%s">Link</a>""" % (
                                                       base_url)
                                              , message_type="notification",
                                              subtype_xmlid="mail.mt_comment",
                                              author_id=user.partner_id.id,
                                              notification_ids=notification_ids,
                                              )
