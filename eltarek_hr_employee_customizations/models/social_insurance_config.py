# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo.http import request


class SocialInsuranceConfig(models.Model):
    _name = 'social.insurance.config'
    _rec_name = 'name'

    name = fields.Char('Name')
    social_number = fields.Char('Social Number')

    @api.constrains('social_number')
    def constrains_truck_number(self):
        truck = self.env['social.insurance.config'].search([('id','!=',self.id)])
        for rec in truck:
            if rec.social_number == self.social_number:
                raise ValidationError('Social Number Must Be Unique')