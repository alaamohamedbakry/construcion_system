from odoo import api, fields, models

class ConstructionBidFile(models.Model):
    _name = "construction.bid.file"
    _description = "Construction Bid File"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Bid File",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        tracking=True,
    )

    tender_id = fields.Many2one(
        "construction.tender",
        string="Tender",
        required=True,
        tracking=True,
        ondelete="cascade",
    )

    boq_id = fields.Many2one(
        "construction.boq",
        string="BOQ",
    )

    estimation_id = fields.Many2one(
        "construction.estimation",
        string="Estimation",
    )

    drawings = fields.Binary(
        string="Drawings",
        attachment=True,
    )
    drawings_filename = fields.Char()

    specifications = fields.Binary(
        string="Specifications",
        attachment=True,
    )
    specifications_filename = fields.Char()

    boq_file = fields.Binary(
        string="BOQ File",
        attachment=True,
    )
    boq_file_filename = fields.Char()

    duration = fields.Integer(
        string="Duration (Days)",
    )

    notes = fields.Text(
        string="Notes",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("uploaded", "Uploaded"),
            ("reviewed", "Reviewed"),
            ("approved", "Approved"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "construction.bid.file"
                ) or "New"
        return super().create(vals_list)
    
    
    def action_upload(self):
        self.write({"state": "uploaded"})


    def action_review(self):
        self.write({"state": "reviewed"})


    def action_approve(self):
        self.write({"state": "approved"})


    def action_reset_to_draft(self):
        self.write({"state": "draft"})