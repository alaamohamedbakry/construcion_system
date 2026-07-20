/** @odoo-module **/

import { Component, onWillStart, onMounted, useState } from "@odoo/owl";

import { registry } from "@web/core/registry";

import { useService } from "@web/core/utils/hooks";

export class ConstructionDashboard extends Component {
  setup() {
    this.orm = useService("orm");

    this.state = useState({
      data: {},
    });

    onWillStart(async () => {
      this.state.data = await this.orm.call(
        "construction.dashboard",

        "get_dashboard_data",

        [],
      );
    });

    onMounted(() => {
      this.renderCharts();
    });
  }

  renderCharts() {
    // =========================
    // Budget vs Actual Chart
    // =========================

    const budgetCanvas = document.getElementById("budgetChart");

    if (budgetCanvas) {
      new Chart(
        budgetCanvas,

        {
          type: "bar",

          data: {
            labels: ["Budget", "Actual Cost"],

            datasets: [
              {
                label: "Amount",

                data: [
                  this.state.data.total_budget,

                  this.state.data.actual_cost,
                ],
              },
            ],
          },

          options: {
            responsive: true,

            maintainAspectRatio: false,
          },
        },
      );
    }

    // =========================
    // Project Progress Chart
    // =========================

    const progressCanvas = document.getElementById("progressChart");

    if (progressCanvas) {
      new Chart(
        progressCanvas,

        {
          type: "doughnut",

          data: {
            labels: ["Running", "Completed", "Delayed"],

            datasets: [
              {
                data: [
                  this.state.data.running_projects,

                  this.state.data.completed_projects,

                  this.state.data.delayed_projects,
                ],
              },
            ],
          },

          options: {
            responsive: true,
          },
        },
      );
    }

    // =========================
    // Cost Distribution Chart
    // =========================

    const costCanvas = document.getElementById("costDistributionChart");

    if (costCanvas) {
      const cost = this.state.data.cost_distribution || {
        labels: [],

        values: [],
      };

      new Chart(
        costCanvas,

        {
          type: "pie",

          data: {
            labels: cost.labels,

            datasets: [
              {
                label: "Cost",

                data: cost.values,
              },
            ],
          },

          options: {
            responsive: true,

            maintainAspectRatio: false,
          },
        },
      );
    }

    // =========================
    // Cash Flow Chart
    // =========================

    const cashCanvas = document.getElementById("cashFlowChart");

    if (cashCanvas) {
      const cash = this.state.data.cash_flow || {
        labels: [],

        values: [],
      };

      new Chart(
        cashCanvas,

        {
          type: "line",

          data: {
            labels: cash.labels,

            datasets: [
              {
                label: "Cash Flow",

                data: cash.values,
              },
            ],
          },

          options: {
            responsive: true,

            maintainAspectRatio: false,
          },
        },
      );
    }

    // =========================
    // Purchase Order Status
    // =========================

    const purchaseCanvas = document.getElementById("purchaseStatusChart");

    if (purchaseCanvas) {
      const purchase = this.state.data.purchase_order_status || {
        draft: 0,

        sent: 0,

        purchase: 0,

        done: 0,

        cancel: 0,
      };

      new Chart(
        purchaseCanvas,

        {
          type: "doughnut",

          data: {
            labels: ["Draft", "Sent", "Purchase", "Done", "Cancelled"],

            datasets: [
              {
                label: "Purchase Orders",

                data: [
                  purchase.draft,

                  purchase.sent,

                  purchase.purchase,

                  purchase.done,

                  purchase.cancel,
                ],
              },
            ],
          },

          options: {
            responsive: true,
          },
        },
      );
    }
  }
}

ConstructionDashboard.template = "construction_system.ConstructionDashboard";

registry.category("actions").add(
  "construction_dashboard",

  ConstructionDashboard,
);
