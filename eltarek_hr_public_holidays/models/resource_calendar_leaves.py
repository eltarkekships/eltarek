from odoo import api, fields, models


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    public_holiday_id = fields.Many2one(
        'hr.holidays.public',
        string='Public_holiday_id',
        required=False)