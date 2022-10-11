# -*- coding: utf-8 -*-
# from odoo import http


# class ElTarekComponentUnitPrice(http.Controller):
#     @http.route('/el_tarek_component_unit_price/el_tarek_component_unit_price', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/el_tarek_component_unit_price/el_tarek_component_unit_price/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('el_tarek_component_unit_price.listing', {
#             'root': '/el_tarek_component_unit_price/el_tarek_component_unit_price',
#             'objects': http.request.env['el_tarek_component_unit_price.el_tarek_component_unit_price'].search([]),
#         })

#     @http.route('/el_tarek_component_unit_price/el_tarek_component_unit_price/objects/<model("el_tarek_component_unit_price.el_tarek_component_unit_price"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('el_tarek_component_unit_price.object', {
#             'object': obj
#         })
