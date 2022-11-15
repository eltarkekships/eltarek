from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo.http import request


class DriverFollowerLine(models.Model):
    _name = 'driver.follower.line'

    driver_follower_id = fields.Many2one('hr.job')
    follower_number = fields.Char('Truck Follower Number')
    name = fields.Char('Name')