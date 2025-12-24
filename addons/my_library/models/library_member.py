from odoo import models, fields, api
# from odoo.exceptions import ValidationError


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    member_id = fields.Many2one('res.partner', string='Member')
    member_email = fields.Char(string='Email')


    _inherits = {'res.partner': 'partner_id'}


    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        ondelete='cascade',
        string='Related Partner'
    )


    date_start = fields.Date('Member Since', default=fields.Date.today)
    date_end = fields.Date('Termination Date')
    member_number = fields.Char('Member ID')
    date_of_birth = fields.Date('Date of Birth')


    @api.onchange('partner_id')
    def _onchange_member_id(self):
        print("trigered")
        if self. partner_id:
            self.member_email = self. partner_id.email
        else:
            self.member_email = False
