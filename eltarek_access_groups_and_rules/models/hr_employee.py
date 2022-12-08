from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

