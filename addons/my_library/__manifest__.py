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
 'version': '14.0.1.0.0',
 'depends': ['contacts'],
 'data': [
     'security/Groups.xml',
     'security/ir.model.access.csv',
     'views/library_book.xml',
     'views/library_book_category_views.xml',
     'views/res_partner_view.xml',
     'views/library_member.xml',
     'views/library_book_rent.xml',
     'wizard/library_book_rent_wizard.xml',
     'wizard/return_wizard.xml',
     'views/library.book.rent.statistics.xml',
     'views/res_setting_config.xml',
     # 'security/library_rules.xml',
 ],
 # 'sequence' : -80,
 }
