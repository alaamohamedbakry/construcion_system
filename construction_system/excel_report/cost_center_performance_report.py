from odoo import fields, models
import io
import base64
import xlsxwriter


class CostCenterPerformanceReport(models.TransientModel):

    _name = "cost.center.performance.report"
    _description = "Cost Center Performance Report"


    name = fields.Char(
        string="Report Name",
        default="Cost Center Performance Report",
        readonly=True,
    )


    def action_export_excel(self):

        self.ensure_one()

        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(
            output,
            {"in_memory": True}
        )

        worksheet = workbook.add_worksheet(
            "Cost Center Performance"
        )


        worksheet.center_horizontally()

        worksheet.set_row(0,28)
        worksheet.set_row(1,22)
        worksheet.set_row(5,22)



        # =====================
        # Formats
        # =====================

        title_format = workbook.add_format({
            "bold":True,
            "font_size":18,
            "font_color":"white",
            "bg_color":"#1F4E78",
            "align":"center",
            "valign":"vcenter",
        })


        report_title_format = workbook.add_format({
            "bold":True,
            "font_size":13,
            "bg_color":"#D9EAD3",
            "border":1,
            "align":"center",
        })


        header_format = workbook.add_format({
            "bold":True,
            "font_color":"white",
            "bg_color":"#4472C4",
            "border":1,
            "align":"center",
        })


        text_format = workbook.add_format({
            "border":1,
        })


        currency_format = workbook.add_format({
            "border":1,
            "num_format":"#,##0.00",
        })


        state_format = workbook.add_format({
            "border":1,
            "align":"center",
        })


        total_text = workbook.add_format({
            "bold":True,
            "bg_color":"#305496",
            "font_color":"white",
            "border":1,
        })


        total_currency = workbook.add_format({
            "bold":True,
            "bg_color":"#305496",
            "font_color":"white",
            "border":1,
            "num_format":"#,##0.00",
        })



        # =====================
        # Header
        # =====================


        company = self.env.company


        worksheet.merge_range(
            "A1:L1",
            company.name,
            title_format
        )


        worksheet.merge_range(
            "A2:L2",
            "Cost Center Performance Report",
            report_title_format
        )



        worksheet.write(
            "A4",
            "Report Date:"
        )

        worksheet.write(
            "B4",
            str(fields.Date.today())
        )



        # =====================
        # Columns
        # =====================


        headers = [

            "Cost Center",
            "Project",
            "Task",
            "Budget",
            "Material Cost",
            "Labor Cost",
            "Purchase Cost",
            "Subcontract Cost",
            "Actual Cost",
            "Remaining Budget",
            "Variance",
            "Status"

        ]


        for col,header in enumerate(headers):

            worksheet.write(
                5,
                col,
                header,
                header_format
            )



        worksheet.set_column("A:A",25)
        worksheet.set_column("B:C",20)
        worksheet.set_column("D:K",18)
        worksheet.set_column("L:L",15)



        # =====================
        # Data
        # =====================


        cost_centers = self.env[
            "construction.cost.center"
        ].search([])


        row = 6


        for center in cost_centers:


            values = [

                center.name or "",
                center.project_id.name or "",
                center.task_id.name or "",
                center.planned_budget or 0,
                center.material_cost or 0,
                center.labor_cost or 0,
                center.purchase_cost or 0,
                center.subcontract_cost or 0,
                center.actual_cost or 0,
                center.remaining_budget or 0,
                center.budget_variance or 0,
                center.state or "",

            ]



            for col,value in enumerate(values):

                if col in [
                    3,4,5,6,7,8,9,10
                ]:

                    worksheet.write_number(
                        row,
                        col,
                        value,
                        currency_format
                    )

                elif col == 11:

                    worksheet.write(
                        row,
                        col,
                        value,
                        state_format
                    )

                else:

                    worksheet.write(
                        row,
                        col,
                        value,
                        text_format
                    )


            row +=1



        # =====================
        # Total
        # =====================


        worksheet.write(
            row,
            0,
            "TOTAL",
            total_text
        )


        totals = [

            sum(cost_centers.mapped("planned_budget")),
            sum(cost_centers.mapped("material_cost")),
            sum(cost_centers.mapped("labor_cost")),
            sum(cost_centers.mapped("purchase_cost")),
            sum(cost_centers.mapped("subcontract_cost")),
            sum(cost_centers.mapped("actual_cost")),
            sum(cost_centers.mapped("remaining_budget")),
            sum(cost_centers.mapped("budget_variance")),

        ]


        for col,value in enumerate(totals,3):

            worksheet.write_number(
                row,
                col,
                value,
                total_currency
            )



        worksheet.freeze_panes(6,0)


        worksheet.autofilter(
            5,
            0,
            row-1,
            11
        )



        workbook.close()


        output.seek(0)


        filename = (
            f"Cost_Center_Performance_{fields.Date.today()}.xlsx"
        )


        attachment = self.env["ir.attachment"].create({

            "name":filename,

            "type":"binary",

            "datas":base64.b64encode(
                output.read()
            ),

            "mimetype":
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

        })


        return {

            "type":"ir.actions.act_url",

            "url":
            f"/web/content/{attachment.id}?download=true",

            "target":"self",

        }