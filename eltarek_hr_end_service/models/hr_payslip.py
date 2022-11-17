from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # @api.model
    # def create(self, vals):
    #     res = super(HrPayslip, self).create(vals)
    #     terminations = self.env['hr.termination'].search([('employee_id', '=', res.employee_id.id),
    #                                                       ('state', '=', 'approved'),
    #                                                       ('termination_date', '>=', res.date_from),
    #                                                       ('termination_date', '<=', res.date_to)])
    #
    #     resignations = self.env['hr.resignation'].search([('employee_id', '=', res.employee_id.id),
    #                                                       ('state', '=', 'approved'),
    #                                                       ('resign_date', '>=', res.date_from),
    #                                                       ('resign_date', '<=', res.date_to)])
    #
    #     suspends = self.env['hr.suspended'].search(
    #         [('employee_id', '=', res.employee_id.id), ('state', '=', 'approved'), '|',
    #          '&', ('date_from', '>=', res.date_from), ('date_from', '<=', res.date_to),
    #          '&', ('date_from', '<=', res.date_from), ('date_to', '>=', res.date_from)])
    #     if suspends and not terminations and not resignations:
    #         raise ValidationError('%s is suspended at this time interval' % res.employee_id.name)
    #     elif terminations:
    #         res.date_to = terminations[0].termination_date
    #     elif resignations:
    #         res.date_to = resignations[0].resign_date
    #
    #     return res