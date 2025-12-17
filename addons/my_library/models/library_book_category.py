from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BookCategory(models.Model):
    _name = 'library.book.category'
    _description = 'Book Category'
    name = fields.Char('Category')
    description = fields.Text('Description')

    name = fields.Char('Category', required=True)

    parent_id = fields.Many2one(
        'library.book.category',
        string='Parent Category',
        ondelete='cascade',
        index=True
    )


    child_ids = fields.One2many(
        'library.book.category',
        'parent_id',
        string='Child Categories'
    )


    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise ValidationError(
                'Error! You cannot create recursive categories.'
            )


    def create_categories(self):
        categ1 = {
            'name': 'Children category 1',
            'description' : 'Description for children category 1'
        }
        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }
        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        record = self.env['library.book.category'].create(parent_category_val)

