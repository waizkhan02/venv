from odoo import models, fields, api

class LibraryBookRent(models.Model):
    _name = 'library.book.rent'
    _description = 'Library Book Rental'

    book_id = fields.Many2one('library.book', string='Book', required=True)
    borrower_id = fields.Many2one('res.partner', string='Borrower', required=True)
    state = fields.Selection([
        ('ongoing', 'Ongoing'),
        ('returned', 'Returned')
    ], string='State', default='ongoing')
    rent_date = fields.Date(string='Rent Date', default=fields.Date.today)
    return_date = fields.Date(string='Return Date')