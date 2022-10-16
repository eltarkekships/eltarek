# -*- coding: utf-8 -*-
from odoo import http

# class MarbellaExistingRfq(http.Controller):
#     @http.route('/marbella_existing_rfq/marbella_existing_rfq/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/marbella_existing_rfq/marbella_existing_rfq/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('marbella_existing_rfq.listing', {
#             'root': '/marbella_existing_rfq/marbella_existing_rfq',
#             'objects': http.request.env['marbella_existing_rfq.marbella_existing_rfq'].search([]),
#         })

#     @http.route('/marbella_existing_rfq/marbella_existing_rfq/objects/<model("marbella_existing_rfq.marbella_existing_rfq"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('marbella_existing_rfq.object', {
#             'object': obj
#         })