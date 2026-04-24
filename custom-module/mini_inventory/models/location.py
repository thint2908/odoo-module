from odoo import models, fields


class Location(models.Model):
    _name = "mini_inventory.location"
    _description = "Mini Inventory Location"
    # _rec_name tells Odoo which field to display when this model
    # is referenced in a Many2one field elsewhere (default is 'name')
    _rec_name = "name"

    name = fields.Char(string="Location Name", required=True)
    code = fields.Char(string="Location Code", required=True)

    # location_type determines the role of this location in stock flows:
    #   internal → real physical warehouse/shelf owned by the company
    #   supplier → virtual origin point when receiving goods from vendors
    #   customer → virtual destination point when delivering to customers
    #   virtual  → scrap, inventory adjustments, losses
    location_type = fields.Selection([
        ('internal', 'Internal'),
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
        ('virtual', 'Virtual / Scrap'),
    ], string="Location Type", required=True, default='internal')

    active = fields.Boolean(
        default=True,
        help="Uncheck to archive this location without deleting it."
    )

    # Computed display name: "Main Warehouse [WH-MAIN]"
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
    )

    def _compute_display_name(self):
        for loc in self:
            loc.display_name = f"{loc.name} [{loc.code}]"