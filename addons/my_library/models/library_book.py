from odoo import models, fields, api , _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import timedelta
import logging  # <--- Import the python logging module

_logger = logging.getLogger(__name__) # <--- Initialize the logger

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    _description = 'Abstract Archive'

    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

    _inherit = ['base.archive']

    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short Title')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    category_id = fields.Many2one('library.book.category', string='Category')
    pages = fields.Integer('Number of Pages')
    notes = fields.Text('Internal Notes')
    description = fields.Html('Description')
    cover = fields.Binary('Book Cover')
    isbn = fields.Char('ISBN')
    old_edition = fields.Many2one('library.book', string='Old Edition')
    # active = fields.Boolean('Active', default=True)
    out_of_print = fields.Boolean('Out of Print?')
    state = fields.Selection([
        ('draft', 'Not Available'),
        ('borrowed', 'Borrowed'),
        ('available', 'Available'),
        ('lost', 'Lost')
    ], string='State')

    cost_price = fields.Float('Book Price', digits=(2 , 2))
    retail_price = fields.Monetary('Retail Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    reader_rating = fields.Float('Reader Average Rating', digits=(4, 2))



    author_ids = fields.Many2many(
        'res.partner',
        string='Authors'
    )


    distributor_ids = fields.Many2many(
        'res.partner',
        'book_distributor_rel',
        'book_id',
        'partner_id',
        string='Distributors'
    )

    publisher_id = fields.Many2one(
        'res.partner',
        string='Publisher',
        ondelete='cascade'
    )

    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True
    )


    count = fields.Integer(related="author_ids.count_books", string="Author Book Count")

    age_days = fields.Integer(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,
        compute_sudo=True
    )

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.context_today(self)
        print("triggeerd")
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 10

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')]
        return (old_state, new_state) in allowed

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    def find_book(self):
        domain = [
            '|',
                '&',    ('name', 'ilike', 'Book Name'),
                        ('pages', '=', 200),
                '&',    ('name', 'ilike', 'Book Name 2'),
                        ('pages', '>', 200)
        ]
        book = self.env['library.book'].search(domain)
        print(book)

    @api.model
    def book_with_multiple_authors(self, all_books):
        def predicate(self):
            if len(book.author_ids) > 1:
                return True
            return False

        return all_books.filter(predicate)



    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)


    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    def make_draft(self):
        self.change_state('draft')

    def _inverse_age(self):
        today = fields.Date.context_today(self)
        for book in self.filtered('date_release'):
            book.date_release = today - timedelta(days=book.age_days)

    def _search_age(self, operator, value):
        today = fields.Date.context_today(self)
        value_days = timedelta(days=value)
        value_date = today - value_days

    def log_all_library_members(self):
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True

        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Book title must be unique.'),
        ('positive_pages', 'CHECK(pages > 0)', 'Number of pages must be positive.')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise ValidationError('Release date must be in the past.')

    def name_get(self):
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            name = '%s (%s)' % (book.name, ', '.join(authors))
            result.append((book.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not (name == '' and operator == 'ilike'):
            args += ['|', '|', '|',
                     ('name', operator, name),
                     ('isbn', operator, name),
                     ('author_ids.name', operator, name)
                     ]
        return super(LibraryBook, self)._name_search(
            name=name, args=args, operator=operator,
            limit=limit, name_get_uid=name_get_uid)

    def post_to_webservices(self,data):
        try:
            req =requests.post('http://my-test-servive.com', data=data, timeout=2)
            content = req.json()
        except IOError:
            error_msg = _("Error, could not post to webservices")
            raise UserError(error_msg)
        return

    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
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
        # Total 3 records (1 parent and 2 child) will be craeted in library.book.category model
        record = self.env['library.book.category'].create(parent_category_val)
        return True

    # Filter recordset
    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        _logger.info('Filtered Books: %s', filtered_books)

    @api.model
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
        return all_books.filtered(predicate)

    # Traversing recordset
    def mapped_books(self):
        all_books = self.search([])
        books_authors = self.get_author_names(all_books)
        _logger.info('Books Authors: %s', books_authors)

    @api.model
    def get_author_names(self, all_books):
        return all_books.mapped('author_ids.name')

    # Sorting recordset
    def sort_books(self):
        all_books = self.search([])
        books_sorted = self.sort_books_by_date(all_books)
        _logger.info('Books before sorting: %s', all_books)
        _logger.info('Books after sorting: %s', books_sorted)

    @api.model
    def sort_books_by_date(self, all_books):
        return all_books.sorted(key='date_release')

    def book_rent (self):
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_('You cannot rent books'))
        rent_as_superuser = self.env['library.book.rent'].sudo()
        rent_as_superuser.create({
            'book_id':self.id,
            'borrower_id': self.env.user.partner_id.id,
        })


#class for respartnwer

class ResPartner(models.Model):
    _inherit = 'res.partner'

    authored_book_ids = fields.Many2many(
        'library.book',
        string='Authored Books'
    )
    distributed_book_ids = fields.Many2many(
        'library.book',
        'book_distributor_rel',
        'partner_id',
        'book_id',
        string='Distributed Books'
    )


    published_book_ids = fields.One2many(
        'library.book',
        'publisher_id',
        string='Published Books'
    )

    count_books = fields.Integer('Number of Authored Books', compute='_compute_count_books')

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)





