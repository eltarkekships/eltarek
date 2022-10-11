# -*- coding: utf-8 -*-
# from odoo import http


# class ElTarekPurchaseAgreementPayment(http.Controller):
#     @http.route('/el_tarek_purchase_agreement_payment/el_tarek_purchase_agreement_payment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/el_tarek_purchase_agreement_payment/el_tarek_purchase_agreement_payment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('el_tarek_purchase_agreement_payment.listing', {
#             'root': '/el_tarek_purchase_agreement_payment/el_tarek_purchase_agreement_payment',
#             'objects': http.request.env['el_tarek_purchase_agreement_payment.el_tarek_purchase_agreement_payment'].search([]),
#         })

#     @http.route('/el_tarek_purchase_agreement_payment/el_tarek_purchase_agreement_payment/objects/<model("el_tarek_purchase_agreement_payment.el_tarek_purchase_agreement_payment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('el_tarek_purchase_agreement_payment.object', {
#             'object': obj
#         })
