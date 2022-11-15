from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo.http import request


class HeavyDriverLine(models.Model):
    _name = 'heavy.driver.line'

    heavy_driver_id = fields.Many2one('hr.job')
    type = fields.Selection([('clark','Clark'),('winch','Winch'),('digger','Digger')],string='Type')
    name = fields.Char('Name')