from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ConstructionTender(models.Model):
    _name='construction.tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description='Construction Tender'

    name = fields.Char(
    string="Tender Reference",
    required=True,
    copy=False,
    tracking=True,
   )

    customer_id = fields.Many2one(
    "res.partner",
    string="Customer",
    required=True,
    tracking=True,
    )

    issue_date = fields.Date(
    string="Issue Date",
    required=True,
    tracking=True,
    )

    submission_date = fields.Date(
    string="Submission Date",
    required=True,
    tracking=True,
    )

    state = fields.Selection([
    ('draft', 'Draft'),
    ('received', 'Received'),
    ('review', 'Under Review'),
    ('submitted', 'Submitted'),
    ('awarded', 'Awarded'),
    ('lost', 'Lost'),
    ('cancel', 'Cancelled'),
   ], default='draft', tracking=True)

    assigned_engineer_id = fields.Many2one(
    "hr.employee",
    string="Assigned Engineer",
    tracking=True)

    estimated_value = fields.Monetary(
    string="Estimated Value",
    currency_field="currency_id",
    tracking=True)

    currency_id = fields.Many2one(
    "res.currency",
    default=lambda self: self.env.company.currency_id)

    notes = fields.Text(
    string="Notes")


    bid_file_id = fields.Many2one(
    "construction.bid.file",
    string="Bid File")

    boq_id = fields.Many2one(
    "construction.boq",
    string="BOQ")

    estimation_id = fields.Many2one(
    "construction.estimation",
    string="Estimation")

    contract_id = fields.Many2one(
    "construction.contract",
    string="Contract")


    _sql_constraints = [
    (
        "unique_tender_reference",
        "unique(name)",
        "Tender Reference must be unique.",
    )]

    @api.constrains("issue_date", "submission_date")
    def _check_dates(self):
       for rec in self:
        if rec.issue_date and rec.submission_date:
            if rec.submission_date <= rec.issue_date:
                raise ValidationError(
                    "Submission Date must be greater than Issue Date."
                )
            

     

   

    def action_submit(self):
        for rec in self:
            rec.state = "submitted"

    def action_award(self):
        for rec in self:
            rec.state = "awarded" 

    def action_reject(self):
        for rec in self:
            rec.state = "awarded"

    def action_review(self):
        for rec in self:
            rec.state = "review"


    def action_recieved(self):
        for rec in self:
            rec.state = "received"