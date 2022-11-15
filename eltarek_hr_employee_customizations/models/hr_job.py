from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo.http import request


class HrJob(models.Model):
    _inherit = 'hr.job'

    is_driver = fields.Boolean('Is Driver')
    is_branched = fields.Boolean('Is Branched')
    driver_type = fields.Selection([('truck_driver', 'Truck Driver'), ('heavy_driver', 'Heavy equipment Driver'), ('driver_follower', 'Truck Driver Follower')],
                                   string='Driver Type')

    heavy_driver_ids = fields.One2many('heavy.driver.line','heavy_driver_id')
    truck_driver_ids = fields.One2many('truck.driver.line','truck_driver_id')
    driver_follower_ids = fields.One2many('driver.follower.line','driver_follower_id')