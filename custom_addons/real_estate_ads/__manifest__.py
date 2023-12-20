{
    "name": "Real Estate Ads",
    "version": "1.0",
    "author": "HASyriAN",
    "website": "https://www.orait.com.sa",
    "description": """
        Real Estate Advertisement, a custom addon for Odoo
    """,
    "application": True,
    "installable": True,
    "category": "Sales",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/property_view.xml",
        "views/property_type_view.xml",
        "views/property_tag_view.xml",
        "views/property_offer_view.xml",
        "views/menu_items.xml",

        # Data
        # Odoo team always recomend using csv files instead of xml files.
        # "data/property_type.xml"
        "data/estate.property.type.csv"
    ],
    "demo": [
        "demo/property_tag.xml"
    ],
    "license": "LGPL-3"
}
