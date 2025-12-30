from odoo import models, fields, api

class libraryRentWizard(models.TransientModel):
    _name = 'library.rent.wizard'
    _description = 'library.rent.wizard'

    borrower_id = fields.Many2one('res.partner', string='Borrower')
    book_ids =  fields.Many2many('library.book', string='Books')

    def add_book_rents(self):
        rentmodel = self.env['library.book.rent']
        for rec in self:
            for book in rec.book_ids:
                rentmodel.create({
                    'borrower_id': rec.borrower_id.id,
                    'book_id': book.id
                })
