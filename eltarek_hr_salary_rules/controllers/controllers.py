# -*- coding: utf-8 -*-
from odoo import http

# class MobiSocialInsurance2Report(http.Controller):
#     @http.route('/mobi_social_insurance2_report/mobi_social_insurance2_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mobi_social_insurance2_report/mobi_social_insurance2_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mobi_social_insurance2_report.listing', {
#             'root': '/mobi_social_insurance2_report/mobi_social_insurance2_report',
#             'objects': http.request.env['mobi_social_insurance2_report.mobi_social_insurance2_report'].search([]),
#         })

#     @http.route('/mobi_social_insurance2_report/mobi_social_insurance2_report/objects/<model("mobi_social_insurance2_report.mobi_social_insurance2_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mobi_social_insurance2_report.object', {
#             'object': obj
#         })