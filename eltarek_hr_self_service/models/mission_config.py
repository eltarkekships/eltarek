from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError, AccessError


class MissionConfig(models.Model):
    _name = 'mission.config'


    city = fields.Char('City')
    value = fields.Char('Value')



