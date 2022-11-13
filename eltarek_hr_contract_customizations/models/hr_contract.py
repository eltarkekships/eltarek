# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import ValidationError
from datetime import date
from dateutil import relativedelta
from odoo.http import request
import logging
from math import ceil

LOGGER = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_type = fields.Selection(
        [('permnant', 'Permnant Contract'), ('temporary', 'Temporary Contract'), ('outsource', 'Outsource'),
         ('freelance', 'Freelance'), ('consultation', 'Consultation')],
        string='Contract Type')
    fixed_insurance = fields.Float(string="Fixed Insurance Amount", required=False, )
    is_insured = fields.Boolean(string="Is Insured?", default=True)
    gross_salary = fields.Float('Gross Salary')
    employee_insurance = fields.Float(string="Employee Insurance ", required=False,compute='compute_company_employee_insurance')
    company_insurance = fields.Float(string="Company Inusrance ", required=False,compute='compute_company_employee_insurance' )
    total_company_employee = fields.Float(string="Total ", required=False,compute='compute_company_employee_insurance' )

    @api.depends('fixed_insurance')
    def compute_company_employee_insurance(self):
        for rec in self:
            if rec.is_insured:
                insurance_fixed = self.env['hr.insurance.year'].search(
                    [('year', '=', str(date.today().year)), ('type', '=', 'fixed')], limit=1)
                if insurance_fixed:
                    rec.employee_insurance = (insurance_fixed.employee_ratio / 100) * rec.fixed_insurance
                    rec.company_insurance = (insurance_fixed.company_ratio / 100) * rec.fixed_insurance
                    rec.total_company_employee = rec.employee_insurance + rec.company_insurance
            else:
                rec.employee_insurance = 0.0
                rec.company_insurance = 0.0
                rec.total_company_employee = 0.0


    def get_employee_over_sixty_rule(self, date_from=None, date_to=None):
        result = self.get_insurance_primary_wage(date_from, date_to)
        employee_birth_date = self.employee_id.birthday
        age = 0
        if employee_birth_date:
            age = ceil(((datetime.now().date() - employee_birth_date).total_seconds()) / (60 * 60 * 24 * 365))
        return result if age >= 60 else 0

    def get_insurance_primary_wage(self, date_from=None, date_to=None):
        date_from_o = fields.Date.from_string(date_from)
        contract = self.env['hr.contract'].browse(self.id)
        if contract.is_insured:
            insurance_fixed = self.env['hr.insurance.year'].search(
                [('year', '=', str(date_from_o.year)), ('type', '=', 'fixed')], limit=1)
            if not insurance_fixed:
                insurance_fixed = self.env['hr.insurance.year'].search([('type', '=', 'fixed')], order="year desc",
                                                                       limit=1)

            max_insurance_amount = insurance_fixed.insurance_amount_max
            min_insurance_amount = insurance_fixed.insurance_amount_min

            if min_insurance_amount <= contract.fixed_insurance <= max_insurance_amount:
                return contract.fixed_insurance
            elif contract.fixed_insurance < min_insurance_amount:
                return min_insurance_amount
            elif contract.fixed_insurance > max_insurance_amount:
                return max_insurance_amount

        else:
            return 0


    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.name = self.employee_id.name

    def contract_end_date_monthly_notify(self):
        contracts = self.sudo().search([('state', '=', 'open')])
        users = self.env['res.users'].search([])
        for contract in contracts:
            if contract.date_end:
                delta = relativedelta.relativedelta(date.today(), contract.date_end)
                if 0 <= delta.months < 1:
                    for user in users:
                        notification_ids = [(0, 0, {
                            'res_partner_id': user.partner_id.id,
                            'notification_type': 'inbox'
                        })]
                        action_id = self.env.ref('hr_contract.action_hr_contract')  # action id
                        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        base_url += '/web#id=%d&amp;view_type=form&amp;model=%s' % (contract.id, self._name)
                        base_url += '&amp;action=%d' % (action_id.id)
                        contract.message_post(record_name='Contract Expire Date',
                                              body="""Contract Will Expire For """ + contract.employee_id.name + """ After """ + str(
                                                  abs(delta.days)) + """ Days
                                                    <br> You can access contract details from here: <br>"""
                                                   + """<a href="%s">Link</a>""" % (
                                                       base_url)
                                              , message_type="notification",
                                              subtype_xmlid="mail.mt_comment",
                                              author_id=user.partner_id.id,
                                              notification_ids=notification_ids,
                                              )
