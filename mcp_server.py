"""Local MCP-style tool server for the support triage system.

This file exposes tools that each specialist agent can call when it needs
real, structured information instead of relying only on model reasoning.
"""

from __future__ import annotations

from autogen_core.tools import FunctionTool


def get_it_status(service: str | None = None) -> str:
    """Return a simple operational status summary for internal services."""
    services = {
        "vpn": "VPN is healthy. No active outage reported.",
        "crm": "CRM is healthy but may require patch validation after updates.",
        "email": "Email service is healthy. No reports of downtime.",
        "printer": "Printing service is running normally for office devices.",
    }
    if service:
        key = service.lower().strip()
        if key in services:
            return services[key]
        return f"No status record found for '{service}'. Please verify the service name or create a ticket."
    return "Current service status: VPN healthy; CRM healthy; Email healthy; Printing healthy."


def open_it_ticket(issue_summary: str, priority: str = "normal") -> str:
    """Create a mock support ticket for IT or technical issues."""
    summary = issue_summary.strip() or "General technical issue"
    ticket_id = "IT-2048"
    return (
        f"Ticket {ticket_id} created for: {summary}. "
        f"Priority: {priority}. Next step: IT will review and contact the requester."
    )


def get_leave_policy() -> str:
    """Return general leave policy guidance for HR."""
    return (
        "Paid leave policy: employees must submit a leave request at least 5 working days in advance, "
        "unless emergency approval applies. Required documentation varies by leave type and may include "
        "manager approval and a doctor's note for medical leave."
    )


def get_employee_benefits() -> str:
    """Return a summary of common employee benefits information."""
    return (
        "Current benefits include medical, dental, vision coverage, 401(k) matching, and annual leave. "
        "Open enrollment occurs in November. Employees can review their benefits in the HR portal."
    )


def lookup_invoice_status(invoice_id: str | None = None) -> str:
    """Return a simplified payment/invoice status response for accounting queries."""
    samples = {
        "INV-1042": "Invoice INV-1042 is outstanding. Amount due: $428.90. Due date: 2026-11-05.",
        "INV-2039": "Invoice INV-2039 was paid in full on 2026-10-18.",
        "INV-7781": "Invoice INV-7781 is pending review by Accounts. Amount: $1,240.00.",
    }
    if invoice_id:
        invoice_key = invoice_id.strip().upper()
        if invoice_key in samples:
            return samples[invoice_key]
        return (
            f"Invoice {invoice_id} was not found in the local status registry. "
            "Please verify the invoice number or contact Accounts support."
        )
    return "Recent invoices: INV-1042 overdue; INV-2039 paid; INV-7781 pending review."


def get_expense_policy() -> str:
    """Return a summary of the reimbursement and expense policy."""
    return (
        "Expense reimbursement policy: submit receipts within 30 days, use approved vendors when possible, "
        "and ensure the business purpose is documented. Travel and software purchases may require manager approval."
    )


def check_office_inventory(item: str | None = None) -> str:
    """Return office supply or desk equipment availability."""
    inventory = {
        "chair": "Office chairs: 4 available in stock; 2 on order.",
        "monitor": "Monitors: 3 available in stock; 1 reserved for IT support.",
        "keyboard": "Keyboards: 8 available in stock.",
        "desk": "Desks: 2 available in stock for new workstations.",
    }
    if item:
        key = item.lower().strip()
        if key in inventory:
            return inventory[key]
        return f"Inventory item '{item}' is not in stock registry. Please contact Administration."
    return "Current inventory snapshot: chairs 4 available; monitors 3 available; keyboards 8 available; desks 2 available."


def get_compliance_policy(topic: str | None = None) -> str:
    """Return a simplified compliance policy overview."""
    policies = {
        "data_handling": "Customer data must be stored in approved systems, restricted to authorized staff, and encrypted at rest and in transit.",
        "retention": "Retention periods follow company policy and legal obligations; expired records are archived or deleted according to retention schedules.",
        "access": "Access to personal or sensitive data is limited to authorized employees with a business need and approved role-based access.",
    }
    if topic:
        key = topic.lower().replace(" ", "_")
        if key in policies:
            return policies[key]
        return (
            f"No specific policy record for '{topic}' was found. The default practice is to route to Compliance "
            "for approved access and retention guidance."
        )
    return "Compliance baseline: restrict access, protect customer data, and follow retention and legal requirements."


IT_TOOLS = [
    FunctionTool(get_it_status, name="get_it_status", description="Check internal service health for VPN, CRM, email, or printers."),
    FunctionTool(open_it_ticket, name="open_it_ticket", description="Create a support ticket for an IT issue."),
]

HR_TOOLS = [
    FunctionTool(get_leave_policy, name="get_leave_policy", description="Return the standard paid-leave policy and required documents."),
    FunctionTool(get_employee_benefits, name="get_employee_benefits", description="Return general benefits information for employees."),
]

ACCOUNTS_TOOLS = [
    FunctionTool(lookup_invoice_status, name="lookup_invoice_status", description="Check invoice status, due dates, and payment history."),
    FunctionTool(get_expense_policy, name="get_expense_policy", description="Return the expense reimbursement policy and approval guidance."),
]

ADMIN_TOOLS = [
    FunctionTool(check_office_inventory, name="check_office_inventory", description="Check stock availability for office furniture and supplies."),
]

COMPLIANCE_TOOLS = [
    FunctionTool(get_compliance_policy, name="get_compliance_policy", description="Return approved compliance guidance for data access, retention, and data handling."),
]


def get_department_tools():
    """Return tool objects keyed by department name."""
    return {
        "IT": IT_TOOLS,
        "HR": HR_TOOLS,
        "Accounts": ACCOUNTS_TOOLS,
        "Administration": ADMIN_TOOLS,
        "Compliance": COMPLIANCE_TOOLS,
    }
