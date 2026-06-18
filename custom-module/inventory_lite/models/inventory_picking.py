from odoo import fields, models


class InventoryPicking(models.Model):
    _name="inventory.picking"
    _description="Inventor Picking"

    name = fields.Char(string="Ref Code", required=True, default="New")
    picking_type = fields.Selection([
        ('incoming', "Incoming"),
        ('outgoing', "Out Going"),
        ('internal', "Internal")
    ], string="Operation Type", required=True)

    source_location_id = fields.Many2one('inventory.location', string="From location", required=True)
    dest_location_id = fields.Many2one('inventory.location', string="To location", required=True)

    move_ids = fields.One2many('inventory.move','picking_id', string="Stock moves")
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ], string="State", default='draft', required=True)