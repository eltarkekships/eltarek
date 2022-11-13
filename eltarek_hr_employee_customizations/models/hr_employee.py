# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hr_code = fields.Char('Hr Code')
    arabic_name = fields.Char('Arabic Name')

    @api.constrains('hr_code')
    def unique_hr_code(self):
        hr_code = self.env['hr.employee'].search([('id','!=',self.id)])
        if hr_code:
            for hr in hr_code:
                if self.hr_code == hr.hr_code:
                    raise ValidationError('HR Code Cannot Be Duplicated')




