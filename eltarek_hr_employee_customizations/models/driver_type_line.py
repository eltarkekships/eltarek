from odoo import fields, models, api, _



class DriverTypeLine(models.Model):
    _name = 'driver.type.line'
    _rec_name = 'truck_number'

    driver_type_id = fields.Many2one('driver.line')
    name = fields.Char('Name')
    truck_number = fields.Char('Truck Number')