from email.policy import default

from odoo import models, fields, api


class library_book_rent(models.Model):
    _name = 'library.book.rent'
    _description = 'library_book_rent.library_book_rent'

    name = fields.Char()
    book_id = fields.Many2one('library.book','book', required=True)
    borrower_id = fields.Many2one('res.partner','borrower', required=True)
    state = fields.Selection([
        ('ongoing', 'Ongoing'),
        ('returned', 'Returned')
        ('lost', 'Lost')
    ],
    'state',
    default = 'ongoing',
    required=True
    )
    rent_date = fields.Date(default=fields.Date.today,string='Rent Date')
    return_date = fields.Date(string='Return Date')

    def book_lost(self):
        self.ensure_one()
        self.state = 'lost'
        book_with_different_context = self.book_id.with_context(avoid_deactivate=True)
        book_with_different_context.sudo().make_lost()

