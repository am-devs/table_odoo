# -*- coding: utf-8 -*-
{
    'name': "conciliacion Bancaria ",


    'description': """
        app para la conciliacion Bancaria de los difrentes empresas con appis aplicadas en los bancos
    """,

    'author': "David Bata",
    'website': "iancarina.com.ve",
    
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],
    # always loaded
    'data': [
        'views/res_banck.xml',
        'views/panel_bank.xml',
        'views/account_journal.xml',
        'views/account_account.xml',
        #'data/task_account_journal.xml',
    ],
    # only loaded in demonstration mode

    'installable': True,
    'application': True,
    

}
