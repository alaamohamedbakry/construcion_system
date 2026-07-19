from odoo import api, fields, models


class ConstructionSubcontractLine(models.Model):
    _name = "construction.subcontract.line"
    _description = "Subcontract Line"

    subcontract_id = fields.Many2one(
        "construction.subcontract",
        ondelete="cascade",
    )

    boq_line_id = fields.Many2one(
        "construction.boq.line",
        string="BOQ Line",
        required=True,
    )

    name = fields.Char(
        related="boq_line_id.name",
        store=True,
    )

    product_id = fields.Many2one(
        related="boq_line_id.product_id",
        store=True,
    )

    uom_id = fields.Many2one(
        related="boq_line_id.uom_id",
        store=True,
    )

    quantity = fields.Float(
        related="boq_line_id.quantity",
        store=True,
    )

    unit_price = fields.Float(
        related="boq_line_id.unit_price",
        store=True,
    )

    amount = fields.Float(
        compute="_compute_amount",
        store=True,
    )

    @api.depends("quantity", "unit_price")
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.quantity * rec.unit_price