from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo.http import request


class TruckDriverLine(models.Model):
    _name = 'truck.driver.line'

    truck_driver_id = fields.Many2one('hr.job')
    truck_number = fields.Char('Truck Number')
    name = fields.Char('Name')