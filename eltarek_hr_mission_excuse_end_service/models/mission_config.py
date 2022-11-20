from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError, AccessError


class MissionConfig(models.Model):
    _name = 'mission.config'
    _rec_name = 'city'


    city = fields.Char('City')
    emp_value = fields.Char('Employee Value')
    manager_value = fields.Char('Manager Value')



