from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Picking(models.Model):
    _name = "mini_inventory.picking"
    _description = "Mini Inventory Picking"

    # copy=False: when duplicating a picking, don't copy the reference number
    name = fields.Char(string="Reference", required=True, copy=False, default="New")

    picking_type = fields.Selection([
        ('incoming', 'Incoming (Goods Receipt)'),
        ('outgoing', 'Outgoing (Delivery)'),
        ('internal', 'Internal Transfer'),
    ], string="Operation Type", required=True)

    location_src_id = fields.Many2one(
        'mini_inventory.location',
        string="From Location",
        required=True,
    )
    location_dest_id = fields.Many2one(
        'mini_inventory.location',
        string="To Location",
        required=True,
    )

    # One picking has many moves — this is the master-detail relationship.
    # 'picking_id' is the field on mini_inventory.move that points back here.
    move_ids = fields.One2many(
        'mini_inventory.move',
        'picking_id',
        string="Stock Moves",
    )

    # State machine:
    #   draft      → just created, can still edit freely
    #   confirmed  → locked in, waiting to be executed
    #   done       → validated, stock has been updated
    #   cancelled  → cancelled, no stock impact
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string="State", default='draft', required=True)

    date = fields.Datetime(string="Scheduled Date", default=fields.Datetime.now)
    date_done = fields.Datetime(string="Effective Date", readonly=True)
    note = fields.Text(string="Notes")

    # Computed summary fields shown in the list view
    move_count = fields.Integer(
        string="Number of Lines",
        compute="_compute_move_count",
    )
    total_qty = fields.Float(
        string="Total Quantity",
        compute="_compute_total_qty",
    )

    # -------------------------------------------------------------------------
    # Computed fields
    # -------------------------------------------------------------------------

    @api.depends('move_ids')
    def _compute_move_count(self):
        for picking in self:
            picking.move_count = len(picking.move_ids)

    @api.depends('move_ids.qty')
    def _compute_total_qty(self):
        for picking in self:
            picking.total_qty = sum(picking.move_ids.mapped('qty'))

    # -------------------------------------------------------------------------
    # onchange: auto-fill move locations when picking locations change
    # -------------------------------------------------------------------------

    @api.onchange('picking_type')
    def _onchange_picking_type(self):
        """Auto-set default locations based on operation type."""
        Location = self.env['mini_inventory.location']
        if self.picking_type == 'incoming':
            self.location_src_id = Location.search(
                [('location_type', '=', 'supplier')], limit=1
            )
            self.location_dest_id = Location.search(
                [('location_type', '=', 'internal')], limit=1
            )
        elif self.picking_type == 'outgoing':
            self.location_src_id = Location.search(
                [('location_type', '=', 'internal')], limit=1
            )
            self.location_dest_id = Location.search(
                [('location_type', '=', 'customer')], limit=1
            )

    # -------------------------------------------------------------------------
    # Sequence: auto-generate reference number on create
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-generate reference like IN/0001, OUT/0001."""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                picking_type = vals.get('picking_type', 'internal')
                prefix = {
                    'incoming': 'IN',
                    'outgoing': 'OUT',
                    'internal': 'INT',
                }.get(picking_type, 'PICK')

                # Count existing pickings of this type to generate next number
                count = self.search_count([('picking_type', '=', picking_type)]) + 1
                vals['name'] = f"{prefix}/{count:04d}"

        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Action buttons (called from XML button clicks)
    # -------------------------------------------------------------------------

    def action_confirm(self):
        """
        Draft → Confirmed.
        Locks the picking so lines can no longer be freely edited.
        """
        self.ensure_one()   # ensure this method is called on exactly 1 record
        if self.state != 'draft':
            raise UserError("Only draft pickings can be confirmed.")
        if not self.move_ids:
            raise UserError("Cannot confirm a picking with no move lines.")
        self.state = 'confirmed'

    def action_validate(self):
        """
        Confirmed → Done.
        This is the key step: checks stock, updates quants, marks moves done.
        """
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError("Only confirmed pickings can be validated.")

        # For outgoing deliveries, check we have enough stock first
        if self.picking_type == 'outgoing':
            self._check_availability()

        # Mark all moves as done
        self.move_ids.write({'state': 'done', 'date': fields.Datetime.now()})

        # Update the quant table (the actual stock ledger)
        self._update_quants()

        self.state = 'done'
        self.date_done = fields.Datetime.now()

    def action_cancel(self):
        """Cancel a picking (allowed from draft or confirmed, not done)."""
        self.ensure_one()
        if self.state == 'done':
            raise UserError("A completed picking cannot be cancelled.")
        self.move_ids.write({'state': 'cancelled'})
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        """Reset a cancelled picking back to draft so it can be edited again."""
        self.ensure_one()
        if self.state != 'cancelled':
            raise UserError("Only cancelled pickings can be reset to draft.")
        self.move_ids.write({'state': 'draft'})
        self.state = 'draft'

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _check_availability(self):
        """
        Check that every outgoing move has enough stock at the source location.
        Raises UserError if any product is short.
        """
        Quant = self.env['mini_inventory.quant']
        errors = []
        for move in self.move_ids:
            quant = Quant.search([
                ('product_id', '=', move.product_id.id),
                ('location_id', '=', move.location_src_id.id),
            ], limit=1)
            available = quant.qty if quant else 0.0
            if available < move.qty:
                errors.append(
                    f"• {move.product_id.name}: need {move.qty}, "
                    f"available {available} at {move.location_src_id.name}"
                )
        if errors:
            raise UserError(
                "Not enough stock to validate this delivery:\n" + "\n".join(errors)
            )

    def _update_quants(self):
        """
        Update mini_inventory.quant records after a successful validation.

        Double-entry logic:
          - Deduct qty from source location  (only if internal)
          - Add qty to destination location  (only if internal)

        Virtual/supplier/customer locations don't have quants —
        they are just accounting endpoints.
        """
        Quant = self.env['mini_inventory.quant']

        for move in self.move_ids:
            # --- Deduct from source ---
            if move.location_src_id.location_type == 'internal':
                src_quant = Quant.search([
                    ('product_id', '=', move.product_id.id),
                    ('location_id', '=', move.location_src_id.id),
                ], limit=1)
                if src_quant:
                    src_quant.qty -= move.qty
                # (if no quant exists at src, it means stock is 0; the
                #  availability check above would have already caught this)

            # --- Add to destination ---
            if move.location_dest_id.location_type == 'internal':
                dest_quant = Quant.search([
                    ('product_id', '=', move.product_id.id),
                    ('location_id', '=', move.location_dest_id.id),
                ], limit=1)
                if dest_quant:
                    dest_quant.qty += move.qty
                else:
                    # First time this product arrives at this location
                    Quant.create({
                        'product_id': move.product_id.id,
                        'location_id': move.location_dest_id.id,
                        'qty': move.qty,
                    })

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------

    @api.constrains('location_src_id', 'location_dest_id')
    def _check_locations_different(self):
        for picking in self:
            if picking.location_src_id == picking.location_dest_id:
                raise ValidationError(
                    "Source and destination locations must be different."
                )