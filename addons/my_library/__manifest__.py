{'name': "My library",
'summary': "Manage books easily",
'description': """
Manage Library
==============
Description related to library.
""",
'author': "waiz khan",
'website': "http://www.example.com",
'category': 'Uncategorized',
'version': '13.0.1',
'depends': ['contacts'],
'data': [
    'security/Groups.xml',
    'security/ir.model.access.csv',
    'views/library_book.xml',
    'views/library_book_category_views.xml',
    'views/res_partner_view.xml',
    'views/library_member.xml',
    # 'security/library_rules.xml',
    ],
 # 'sequence' : -80,
 }