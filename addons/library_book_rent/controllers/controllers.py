# -*- coding: utf-8 -*-
# from odoo import http


# class LibraryBookRent(http.Controller):
#     @http.route('/library_book_rent/library_book_rent/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/library_book_rent/library_book_rent/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('library_book_rent.listing', {
#             'root': '/library_book_rent/library_book_rent',
#             'objects': http.request.env['library_book_rent.library_book_rent'].search([]),
#         })

#     @http.route('/library_book_rent/library_book_rent/objects/<model("library_book_rent.library_book_rent"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('library_book_rent.object', {
#             'object': obj
#         })
