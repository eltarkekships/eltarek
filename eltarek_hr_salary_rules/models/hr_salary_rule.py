from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import ValidationError
from datetime import date
from dateutil import relativedelta
from odoo.http import request
import logging
import calendar
from datetime import timedelta


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    contract_valid_based = fields.Boolean(default=False,
                                          help="If this field is set the salary rule rate will be affected by the start and end dates of the contract.")
    is_analytic = fields.Boolean('Is Analytic')
