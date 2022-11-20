from odoo import models, fields, api, _


class HrVariableAllowanceDeduction(models.Model):
    _name = 'hr.variable.allowance.deduction'

    employee_id = fields.Many2one('hr.employee')
    contract_id = fields.Many2one('hr.contract', compute='_get_contract_id', store=True)
    date = fields.Date()
    amount = fields.Float()
    hour_day_amounts = fields.Float('Variable')
    type = fields.Many2one('hr.variable.allowance.deduction.type')
    payslip_id = fields.Many2one('hr.payslip')

    @api.depends('employee_id')
    def _get_contract_id(self):
        running_contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                           ('state', '=', 'open')])
        if running_contracts:
            self.contract_id = running_contracts[0].id

    @api.onchange('type')
    def _set_amount(self):
        if self.type and self.contract_id:
            if self.type.calculation_method == 'fixed':
                self.amount = self.type.fixed_amount * self.hour_day_amounts
            elif self.type.calculation_method == 'percentage':
                self.amount = self.contract_id.wage * self.type.percentage_amount * 0.01 * self.hour_day_amounts
            elif self.type.calculation_method == 'work_day':
                self.amount = (self.contract_id.wage / self.contract_id.num_work_day_per_month) * self.type.work_day_amount * self.hour_day_amounts
            elif self.type.calculation_method == 'work_hour':
                total = (self.contract_id.num_work_day_per_month * self.contract_id.num_work_hour_per_day)
                self.amount = (self.contract_id.wage / total) * self.type.work_hour_amount * self.hour_day_amounts

            # if self.type.type == 'deduction':
            #     self.amount *= -1


