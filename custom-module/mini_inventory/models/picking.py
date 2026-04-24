from odoo import models, fields, api
from odoo.exceptions import UserError

class Picking(models.Model):
    _name = "mini_inventory.picking"
    _description = "Mini Inventory Picking"
    
    name = fields.Char(string="Reference", required=True, copy=False)
    picking_type = fields.Selection([
        ('incoming', "Incoming"),
        ('outgoing', 'Outgoing'),
        ('internal', 'Internal Transfer'),
    ], string="Operation Type", required=True)
    location_src_id = fields.Many2one('mini_inventory.location', string="From Location", required=True)
    location_dest_id = fields.Many2one('mini_inventory.location', string="To Location", required=True)
    move_ids = fields.One2many('mini_inventory.move', 'product_id', string="Stock Move")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('comfirmed', "Comfirmed"),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string="State", default='draft', required=True)
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    note = fields.Text(string="Notes")
    
    def action_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError("Only draft pickings can be confirmed")
        if not self.move_ids:
            raise UserError("Cannot confirm a picking with no moves.")
        self.move_ids.write({'state': 'done'})
        self.state = 'comfirmed'
        
    def action_validate(self):
        self.ensure_one()
        if self.state != 'comfirmed':
            raise UserError("Only confirmed pickings can be validated")
        if self.picking_type == 'outgoing':
            self._check_availability()
        self.move_ids.write({'state': 'done'})
        self.state = 'done'
        self._update_quants()
        
    def action_cancel(self):
        self.ensure_one()
        if self.state == 'done':
            raise UserError("Cannot cancel a picking that is already done.")
        self.move_ids.write({'state': 'cancelled'})
        self.state = 'cancelled'
        
    def _check_availability(self):
        for move in self.move_ids:
            quant = self.env['mini_inventory,quant'].search([
                ('product_id', '=', move.product_id.id),
                ('location_id', '=', move.location_id.id),
            ], limit=1)
            available = quant.qty if quant else 0.0
            if available < move.qty:
                raise UserError(f"Not enough stock for '{move.product_id}', "
                                f"Available: {available}, Required: {move.qty}")

    def _update_quants(self):
        Quant = self.env['mini_inventory.quant']
        for move in self.move_ids:
            #TRu kho nguon chi cos internal location moi co quant
            if move.location_src_id.location_type == 'internal':
                src_quant = Quant.search([
                    ('product_id', '=', move.product_id.id),
                    ('location_id', '=', move.location_id.id),
                ], limit=1)
                if src_quant:
                    src_quant.qty -= move.qty
                    
            # cong kho dich
            if move.location_dest_id.location_type == 'internal':
                dest_quant = Quant.search([
                    ('product_id', '=', move.product_id.id),
                    ('location_id', '=', move.location_dest_id.id),
                ], limit=1)
                if dest_quant:
                    dest_quant.qty += move.qty
                else:
                    # chua co quant tai location nay -> tao moi
                    Quant.create({
                        'product_id': move.product_id.id,
                        'location_id': move.location_id.id,
                        'qty': move.qty,
                    })
