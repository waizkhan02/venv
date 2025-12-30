from odoo import models, fields, api


class library_book_rent(models.Model):
    _name = 'library.book.rent'
    _description = 'library_book_rent.library_book_rent'

    active = fields.Boolean(default=True)
    name = fields.Char()
    book_id = fields.Many2one('library.book','book', required=True)
    borrower_id = fields.Many2one('res.partner','borrower', required=True)
    state = fields.Selection([
        ('ongoing', 'Ongoing'),
        ('returned', 'Returned'),
        ('lost', 'Lost')
    ],
    'state',
    default = 'ongoing',
    required=True
    )
    rent_date = fields.Date(default=fields.Date.today,string='Rent Date')
    return_date = fields.Date(string='Return Date')

    @api.model
    def create(self, vals):
        book_rec = self.env['library.book'].browse(vals['book_id'])  # returns record set from for given id
        book_rec.make_borrowed()
        return super(library_book_rent, self).create(vals)

    def book_return(self):
        self.ensure_one()
        self.book_id.make_available()
        self.write({
            'state': 'returned',
            'return_date': fields.Date.today()
        })

    def book_lost(self):
        self.ensure_one()
        self.write({'state': 'lost'})
        book_with_different_context = self.book_id.with_context(avoid_deactivate=True)
        book_with_different_context.sudo().make_lost()

