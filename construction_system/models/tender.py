from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ConstructionTender(models.Model):
    _name = "construction.tender"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Construction Tender"

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

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("received", "Received"),
            ("review", "Under Review"),
            ("submitted", "Submitted"),
            ("awarded", "Awarded"),
            ("lost", "Lost"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    assigned_engineer_id = fields.Many2one(
        "hr.employee", string="Assigned Engineer", tracking=True
    )

    estimated_value = fields.Monetary(
        string="Estimated Value", currency_field="currency_id", tracking=True
    )

    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )

    notes = fields.Text(string="Notes")

    bid_file_ids = fields.One2many(
        "construction.bid.file", "tender_id", string="Bid Files"
    )
    boq_ids = fields.One2many("construction.boq", "tender_id", string="BOQs")

    estimation_ids = fields.One2many(
        "construction.estimation", "tender_id", string="Estimations"
    )

    estimation_count = fields.Integer(compute="_compute_estimation_count")

    contract_ids = fields.One2many(
        "construction.contract", "tender_id", string="Contracts"
    )

    bid_file_count = fields.Integer(compute="_compute_bid_file_count")
    boq_count = fields.Integer(compute="_compute_boq_count")
    estimation_count = fields.Integer(compute="_compute_estimation_count")
    contract_count = fields.Integer(compute="_compute_contract_count")

    _sql_constraints = [
        (
            "unique_tender_reference",
            "unique(name)",
            "Tender Reference must be unique.",
        )
    ]

    @api.constrains("issue_date", "submission_date")
    def _check_dates(self):
        for rec in self:
            if rec.issue_date and rec.submission_date:
                if rec.submission_date <= rec.issue_date:
                    raise ValidationError(
                        "Submission Date must be greater than Issue Date."
                    )

    def action_recieved(self):
        for rec in self:
            rec.state = "received"

    def action_review(self):
        for rec in self:
            rec.state = "review"

    def action_submit(self):
        for rec in self:
            rec.state = "submitted"

    def action_award(self):
        for rec in self:
            rec.state = "awarded"
          

    def action_reject(self):
        for rec in self:
            rec.state = "lost"

    @api.depends("bid_file_ids")
    def _compute_bid_file_count(self):
        for rec in self:
            rec.bid_file_count = len(rec.bid_file_ids)

    @api.depends("boq_ids")
    def _compute_boq_count(self):
        for rec in self:
            rec.boq_count = len(rec.boq_ids)

    @api.depends("contract_ids")
    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.contract_ids)

    def action_open_bid_file(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "construction_system.action_construction_bid_file"
        )
        action["context"] = {"default_tender_id": self.id}

        bid_files = self.bid_file_ids
        if len(bid_files) > 1:
            action["domain"] = [("id", "in", bid_files.ids)]
        elif len(bid_files) == 1:
            action["views"] = [
                (
                    self.env.ref("construction_system.construction_bid_file_form").id,
                    "form",
                )
            ]
            action["res_id"] = bid_files.id
        else:
            action["domain"] = [("tender_id", "=", self.id)]
        return action

    def action_open_boq(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "construction_system.action_construction_boq"
        )
        action["context"] = {"default_tender_id": self.id}

        boqs = self.boq_ids
        if len(boqs) > 1:
            action["domain"] = [("id", "in", boqs.ids)]
        elif len(boqs) == 1:
            action["views"] = [
                (
                    self.env.ref("construction_system.view_construction_boq_form").id,
                    "form",
                )
            ]
            action["res_id"] = boqs.id
        else:
            action["domain"] = [("tender_id", "=", self.id)]
        return action

    def action_open_contract(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "construction_system.action_construction_contract"
        )
        action["context"] = {"default_tender_id": self.id}

        contracts = self.contract_ids
        if len(contracts) > 1:
            action["domain"] = [("id", "in", contracts.ids)]
        elif len(contracts) == 1:
            action["views"] = [
                (
                    self.env.ref(
                        "construction_system.view_construction_contract_form"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = contracts.id
        else:
            action["domain"] = [("tender_id", "=", self.id)]
        return action

    @api.depends("estimation_ids")
    def _compute_estimation_count(self):
        for rec in self:
            rec.estimation_count = len(rec.estimation_ids)

    def action_open_estimation(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "construction_system.action_construction_estimation"
        )

        action["context"] = {
            "default_tender_id": self.id,
        }

        estimations = self.estimation_ids

        if len(estimations) > 1:
            action["domain"] = [("id", "in", estimations.ids)]
        elif len(estimations) == 1:
            action["views"] = [
                (
                    self.env.ref("construction_system.construction_estimation_form").id,
                    "form",
                )
            ]
            action["res_id"] = estimations.id
        else:
            action["domain"] = [("tender_id", "=", self.id)]

            return action
        

    def action_create_estimation(self):
        self.ensure_one()

        estimation = self.env['construction.estimation'].create({
            'tender_id': self.id,
        })

        return {
        'type': 'ir.actions.act_window',
        'res_model': 'construction.estimation',
        'view_mode': 'form',
        'res_id': estimation.id,
        }
