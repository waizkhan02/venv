from odoo import models, fields, api , _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import timedelta

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
    pages = fields.Integer('Number of Pages')
    notes = fields.Text('Internal Notes')
    description = fields.Html('Description')
    cover = fields.Binary('Book Cover')
    # active = fields.Boolean('Active', default=True)
    out_of_print = fields.Boolean('Out of Print?')
    state = fields.Selection([
        ('draft', 'Not Available'),
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
                   ('available', 'lost'),
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
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release or '')
            result.append((record.id, rec_name))
        return result

    def post_to_webservices(self,data):
        try:
            req =requests.post('http://my-test-servive.com', data=data, timeout=2)
            content = req.json()
        except IOError:
            error_msg = _("Error, could not post to webservices")
            raise UserError(error_msg)
        return content


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





