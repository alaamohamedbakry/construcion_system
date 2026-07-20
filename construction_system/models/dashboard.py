from odoo import api, fields, models


class ConstructionDashboard(models.TransientModel):
    _name = "construction.dashboard"
    _description = "Construction Executive Dashboard"

    # =====================================================
    # KPI Fields
    # =====================================================

    total_projects = fields.Integer(compute="_compute_dashboard")
    running_projects = fields.Integer(compute="_compute_dashboard")
    completed_projects = fields.Integer(compute="_compute_dashboard")
    delayed_projects = fields.Integer(compute="_compute_dashboard")

    total_budget = fields.Float(compute="_compute_dashboard")
    actual_cost = fields.Float(compute="_compute_dashboard")
    remaining_budget = fields.Float(compute="_compute_dashboard")
    total_profit = fields.Float(compute="_compute_dashboard")
    material_cost = fields.Float(compute="_compute_dashboard")

    purchase_orders = fields.Integer(compute="_compute_dashboard")
    material_requests = fields.Integer(compute="_compute_dashboard")
    cost_centers = fields.Integer(compute="_compute_dashboard")
    progress_billings = fields.Integer(compute="_compute_dashboard")

    # =====================================================
    # Advanced Dashboard Data
    # =====================================================

    cost_distribution = fields.Json(compute="_compute_dashboard")

    cash_flow = fields.Json(compute="_compute_dashboard")

    purchase_order_status = fields.Json(compute="_compute_dashboard")

    critical_tasks = fields.Json(compute="_compute_dashboard")

    open_purchase_orders = fields.Json(compute="_compute_dashboard")

    # NEW
    top_cost_centers = fields.Json(compute="_compute_dashboard")

    project_profitability = fields.Json(compute="_compute_dashboard")

    # =====================================================
    # Dashboard Values
    # =====================================================

    def _get_dashboard_values(self):

        Project = self.env["project.project"]
        CostCenter = self.env["construction.cost.center"]
        MaterialRequest = self.env["construction.material.request"]
        PurchaseOrder = self.env["purchase.order"]
        ProgressBilling = self.env["construction.progress.billing"]
        Task = self.env["project.task"]
        AccountMove = self.env["account.move"]

        today = fields.Date.today()

        # -----------------------------
        # Fetch Data
        # -----------------------------

        projects = Project.search([])
        centers = CostCenter.search([])
        all_billings = ProgressBilling.search([])

        # -----------------------------
        # Cost
        # -----------------------------

        total_budget = sum(centers.mapped("planned_budget"))
        actual_cost = sum(centers.mapped("actual_cost"))
        remaining_budget = sum(centers.mapped("remaining_budget"))

        material_cost = sum(centers.mapped("material_cost"))
        labor_cost = sum(centers.mapped("labor_cost"))
        purchase_cost = sum(centers.mapped("purchase_cost"))
        subcontract_cost = sum(centers.mapped("subcontract_cost"))

        # -----------------------------
        # Revenue
        # -----------------------------

        revenue = sum(all_billings.mapped("current_billing_amount"))

        # -----------------------------
        # Cost Distribution
        # -----------------------------

        cost_distribution = {
            "labels": [
                "Material",
                "Labor",
                "Purchase",
                "Subcontract",
            ],
            "values": [
                material_cost,
                labor_cost,
                purchase_cost,
                subcontract_cost,
            ],
        }

        # -----------------------------
        # Cash Flow
        # -----------------------------

        cash_flow = {
            "labels": [],
            "values": [],
        }

        for billing in all_billings:
            if billing.billing_date:
                cash_flow["labels"].append(str(billing.billing_date))
                cash_flow["values"].append(
                    billing.current_billing_amount
                )

        # -----------------------------
        # Project Progress
        # -----------------------------

        project_progress = {}

        for billing in all_billings:

            if billing.project_id:

                current = project_progress.get(
                    billing.project_id.id,
                    0,
                )

                project_progress[
                    billing.project_id.id
                ] = max(
                    current,
                    billing.progress_percentage,
                )

        # -----------------------------
        # Projects KPI
        # -----------------------------

        running_projects = 0
        completed_projects = 0
        delayed_projects = 0

        for project in projects:

            progress = project_progress.get(
                project.id,
                0,
            )

            if progress >= 100:
                completed_projects += 1

            elif progress > 0:
                running_projects += 1

            end_date = False

            if hasattr(project, "date_end"):
                end_date = project.date_end

            elif hasattr(project, "date"):
                end_date = project.date

            if (
                end_date
                and end_date < today
                and progress < 100
            ):
                delayed_projects += 1      
        # -----------------------------
        # Purchase Order Status
        # -----------------------------

        purchase_status = {
            "draft": 0,
            "sent": 0,
            "purchase": 0,
            "done": 0,
            "cancel": 0,
        }

        orders = PurchaseOrder.search([])

        for po in orders:
            if po.state in purchase_status:
                purchase_status[po.state] += 1

        # -----------------------------
        # Critical Tasks
        # -----------------------------

        critical_tasks = []

        for task in Task.search(
            [("stage_id.fold", "=", False)],
            limit=10,
        ):

            critical_tasks.append({
                "name": task.name,
                "project": task.project_id.name if task.project_id else "",
                "deadline": str(task.date_deadline) if task.date_deadline else "",
            })

        # -----------------------------
        # Open Purchase Orders
        # -----------------------------

        open_purchase_orders = []

        for po in PurchaseOrder.search(
            [
                (
                    "state",
                    "in",
                    ["draft", "sent", "purchase"],
                )
            ],
            limit=10,
        ):

            open_purchase_orders.append({
                "name": po.name,
                "vendor": po.partner_id.name,
                "amount": po.amount_total,
                "state": po.state,
            })

        # -----------------------------
        # Top Cost Centers
        # -----------------------------

        top_cost_centers = []

        for center in CostCenter.search(
            [],
            order="actual_cost desc",
            limit=10,
        ):

            top_cost_centers.append({
                "name": center.name,
                "budget": center.planned_budget,
                "actual": center.actual_cost,
                "remaining": center.remaining_budget,
            })

        # -----------------------------
        # Project Profitability
        # -----------------------------
                # -----------------------------
        # Project Profitability
        # -----------------------------

        project_profitability = []

        for project in projects:

            customer_invoices = AccountMove.search([
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("project_id", "=", project.id),
            ])

            project_revenue = sum(
                customer_invoices.mapped("amount_untaxed")
            )

            project_cost = sum(
                CostCenter.search([
                    ("project_id", "=", project.id)
                ]).mapped("actual_cost")
            )

            project_profitability.append({
                "name": project.name,
                "revenue": project_revenue,
                "cost": project_cost,
                "profit": project_revenue - project_cost,
            })

            customer_revenue = sum(
            AccountMove.search([
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
            ]).mapped("amount_untaxed"))

        return {
            # KPI
            "total_projects": len(projects),
            "running_projects": running_projects,
            "completed_projects": completed_projects,
            "delayed_projects": delayed_projects,

            "cost_centers": len(centers),

            "total_budget": total_budget,
            "actual_cost": actual_cost,
            "remaining_budget": remaining_budget,

            "material_cost": material_cost,

            "total_profit": customer_revenue - actual_cost,

            "material_requests": MaterialRequest.search_count([]),

            "purchase_orders": PurchaseOrder.search_count([]),

            "progress_billings": len(all_billings),

            # Charts
            "cost_distribution": cost_distribution,
            "cash_flow": cash_flow,
            "purchase_order_status": purchase_status,

            # Tables
            "critical_tasks": critical_tasks,
            "open_purchase_orders": open_purchase_orders,
            "top_cost_centers": top_cost_centers,
            "project_profitability": project_profitability,
        }

    # =====================================================
    # Compute
    # =====================================================

    @api.depends()
    def _compute_dashboard(self):

        for rec in self:

            values = rec._get_dashboard_values()

            for field_name, value in values.items():
                setattr(rec, field_name, value)

    # =====================================================
    # OWL
    # =====================================================

    @api.model
    def get_dashboard_data(self):

        return self._get_dashboard_values()