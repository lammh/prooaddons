{
    "name" : "Tunisian Taxes",
    "version" : "1.3",
    'sequence': 2,
    "depends" : ["account_voucher", "l10n_tn"],
    "author" : "ProoSoft",
    'complexity': "easy",

    "description": """
    Supports withholding and stamp tax.
    """,

    "website" : "http://www.ProoSoft.com",
    "category" : "Accounting & Finance",
    "data" : [
        "res_config_view.xml",
        "taxes_view.xml",
        "withholding_customer_view.xml",
        "withholding_supplier_view.xml",
    ],
    "auto_install": False,
    "installable": True,
}

