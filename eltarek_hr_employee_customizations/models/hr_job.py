from odoo import fields, models, api, _



class HrJob(models.Model):
    _inherit = 'hr.job'

    is_driver = fields.Boolean('Is Driver')
    driver_line_ids = fields.One2many('driver.line','driver_id')
