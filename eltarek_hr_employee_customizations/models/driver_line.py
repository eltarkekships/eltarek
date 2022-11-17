from odoo import fields, models, api, _



class DriverLine(models.Model):
    _name = 'driver.line'
    _rec_name = 'type_id'

    driver_id = fields.Many2one('hr.job')
    type_id = fields.Many2one('hr.driver.type')
    driver_type_ids = fields.One2many('driver.type.line', 'driver_type_id')
