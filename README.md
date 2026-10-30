# Northstar Support

A local multi-agent customer support system built with Python, Streamlit, and AutoGen. The app routes each user request to the most relevant specialist team and gives each team a focused set of tools for more accurate answers.

## Overview

This project simulates an internal support center with five specialist departments:

- IT Support
- Compliance
- Administration
- Human Resources
- Accounts & Finance

The app uses a manager agent to decide which department should handle each message. That department then responds with domain-specific guidance and can call local tools for structured business facts such as:

- invoice status lookups
- office inventory checks
- leave policy information
- compliance data-handling guidance
- internal service status checks

## Why this project exists

The goal is to demonstrate a practical multi-agent support workflow in a small, local environment:

- a user-facing chat interface
- a routing agent that decides which team owns the request
- specialized agents that answer within their domain
- tool-backed actions that improve factual accuracy
- resilient department parsing when the manager responds with natural language instead of a strict label

## Architecture

### 1. Front end
The Streamlit app in `app.py` provides the conversation UI and handles the chat loop.

### 2. Manager / router agent
The manager decides the likely department for the latest request. It is instructed to return a single exact label such as:

- IT
- Compliance
- Administration
- HR
- Accounts

### 3. Specialist agents
Each department has a dedicated agent with instructions tailored to that support domain.

### 4. Local MCP-style tool server
The file `mcp_server.py` exposes a lightweight tool layer. It gives each specialist domain-specific functions such as:

- `get_it_status()`
- `open_it_ticket()`
- `get_leave_policy()`
- `get_employee_benefits()`
- `lookup_invoice_status()`
- `get_expense_policy()`
- `check_office_inventory()`
- `get_compliance_policy()`

These tools are attached to the proper department agent so the model can answer with grounded operational data, not only generic reasoning.

## Supported departments

### IT Support
Handles:

- software issues
- hardware issues
- VPN / login / access problems
- printer and device troubleshooting
- application crashes

### Compliance
Handles:

- privacy and customer-data handling
- access controls
- retention policies
- security and regulatory guidance

### Administration
Handles:

- office furniture and supplies
- workspace and access logistics
- facilities requests
- office inventory checks

### Human Resources
Handles:

- leave policy and paid time off
- employee benefits
- onboarding and workplace policies
- hiring-related questions

### Accounts & Finance
Handles:

- invoices
- billing issues
- expense reimbursement
- refund and payment policy questions

## Project structure

```text
.
├── app.py                 # Streamlit UI and agent orchestration
├── mcp_server.py         # Local MCP-style tool definitions for each department
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── .env                  # Local environment variables (not committed)
├── README.md             # Project documentation
└── .venv                 # Optional local virtual environment
```

## Requirements

- Python 3.10+
- OpenAI API key
- internet access to call the OpenAI model

## Local setup

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:

```bash
cp .env.example .env
```

4. Add your OpenAI credentials:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

You can change the model value to another supported OpenAI-compatible model if needed.

## Run the app

Start the Streamlit interface from the project root:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:8501
```

## Example requests

### IT
- “My CRM app is crashing after the latest update.”
- “The VPN is failing and I cannot connect.”
- “The office printer is offline.”

### Compliance
- “What is our policy for handling customer data and who can access it?”
- “What should we do if a data breach is suspected?”
- “Who can access sensitive customer information?”

### Administration
- “Can you check whether we have office supplies in stock?”
- “I need a new office chair and a spare monitor for my desk.”
- “I need workspace access for a new team member.”

### HR
- “How do I request paid leave and what documents are required?”
- “What are my employee benefits?”
- “What is the leave policy for medical absences?”

### Accounts
- “What is the status of invoice INV-1042?”
- “My invoice looks incorrect for this month.”
- “What is the expense reimbursement policy?”

## Routing behavior

The router is intentionally resilient. It does not assume the manager output will be a strict label. In practice, a model may respond like:

- “The best department is Compliance.”
- “This fits the HR team.”
- “Administration seems like the right team.”

The app normalizes those natural-language responses and also falls back to scanning the user prompt for department keywords if needed. This prevents a common class of routing failures that occur with LLM-generated free text.

## Tools and tool usage

Each specialist agent is given the tools most relevant to its domain:

- IT: service health and ticket creation
- HR: leave and benefits policies
- Accounts: invoice status and expense policy
- Administration: office inventory checks
- Compliance: policy guidance

This allows the system to answer grounded operational questions with more confidence than a general-purpose assistant alone.

## Troubleshooting

### Missing API key
If the app says the API key is required, confirm the `.env` file exists and contains a valid `OPENAI_API_KEY`.

### API or model errors
If the chat fails with a model or API error, check:

- your OpenAI key is valid
- your account has access to the selected model
- your environment is connected to the internet
- the model name in `.env` is supported

### Unknown department errors
The app includes fallback logic to recover from natural-language routing responses. If a prompt still fails, it usually means the model returned something outside the expected department labels, so the app uses keyword detection on the user message as a safety net.

### Streamlit not launching
Make sure you installed dependencies in the active environment and are running the command from the project folder:

```bash
streamlit run app.py
```

## Notes for extension

This project is intentionally structured so it can be extended in a few ways:

- replace the mock local tools with a real external MCP server
- add more departments or sub-teams
- log conversations and route outcomes
- add authentication or authorization for internal use

## License

This project is intended for educational and local demo use. Add your own project license if you plan to distribute or deploy it beyond internal learning.

## Summary

Northstar Support demonstrates a compact but realistic enterprise support workflow with department routing, specialist agents, and tool-powered knowledge retrieval. It is a strong starting point for building more advanced multi-agent internal operations systems.
