"""Streamlit customer support chat backed by an AutoGen agent router."""

import asyncio
import os
import re

import streamlit as st
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

from mcp_server import get_department_tools


load_dotenv()

st.set_page_config(
    page_title="Northstar Support",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEPARTMENTS = {
    "IT": {
        "name": "IT Support",
        "instructions": (
            "You are the IT support specialist. Help with software, hardware, "
            "accounts, and technical troubleshooting. Give clear, safe steps; "
            "ask focused questions when details are missing. Never claim to "
            "have accessed or changed a user's device or account."
        ),
    },
    "Compliance": {
        "name": "Compliance",
        "instructions": (
            "You are the compliance specialist. Help explain internal security "
            "policies, regulatory processes, and compliance requirements in "
            "plain language. Distinguish general information from legal advice "
            "and recommend the appropriate compliance or legal contact when needed."
        ),
    },
    "Administration": {
        "name": "Administration",
        "instructions": (
            "You are the administration specialist. Help with office facilities, "
            "supplies, access logistics, and general operational questions. "
            "Ask for the relevant office or location when it affects the answer."
        ),
    },
    "HR": {
        "name": "Human Resources",
        "instructions": (
            "You are the HR specialist. Help with employee relations, payroll, "
            "benefits, hiring, and workplace processes. Be empathetic and "
            "privacy-conscious; do not ask users to share sensitive personal data."
        ),
    },
    "Accounts": {
        "name": "Accounts & Finance",
        "instructions": (
            "You are the accounts specialist. Help with billing, invoices, "
            "expenses, reimbursements, and finance processes. Never ask for full "
            "payment-card or bank-account details; clarify the relevant invoice "
            "or process without requesting sensitive information."
        ),
    },
}

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
DEPARTMENT_TOOLS = get_department_tools()

DEPARTMENT_KEYWORDS = {
    "IT": [
        "IT", "IT SUPPORT", "TECHNICAL", "SOFTWARE", "HARDWARE",
        "NETWORK", "PASSWORD", "LOGIN", "VPN", "DEVICE",
        "LAPTOP", "PRINTER", "CRM", "APP CRASH", "APPLICATION",
        "SYSTEM ERROR", "SYSTEM", "EMAIL ACCESS", "WORK ACCOUNT"
    ],
    "Compliance": [
        "COMPLIANCE", "SECURITY", "PRIVACY", "DATA POLICY", "LEGAL",
        "REGULATORY", "REGULATION", "DATA RETENTION", "DATA BREACH",
        "SENSITIVE DATA", "PERSONAL DATA", "GDPR", "POLICY"
    ],
    "Administration": [
        "ADMINISTRATION", "OFFICE", "FACILITIES", "SUPPLIES", "DESK",
        "MONITOR", "WORKSPACE", "CONFERENCE ROOM", "BUILDING", "ACCESS",
        "ROOM", "SEATING", "CHAIR", "OFFICE CHAIR", "SPARE MONITOR"
    ],
    "HR": [
        "HR", "HUMAN RESOURCES", "BENEFITS", "PAYROLL", "LEAVE",
        "EMPLOYEE RELATIONS", "HIRING", "RECRUITING", "WORKPLACE",
        "PAID LEAVE", "EMPLOYEE"
    ],
    "Accounts": [
        "ACCOUNTS", "FINANCE", "BILLING", "INVOICE", "EXPENSE",
        "REIMBURSEMENT", "PAYMENT", "COST", "RECEIPT", "REFUND",
        "BANKING", "ACCOUNTS AND FINANCE"
    ],
}


def normalize_department(raw_text: str | None) -> str:
    """Convert free-form router output into a supported department label."""
    if not raw_text:
        return ""

    text = raw_text.upper().replace("&", " AND ")
    text = re.sub(r"[^A-Z0-9 AND/\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    explicit_label = re.search(
        r"(?:^| )(?:THE )?(?:BEST )?DEPARTMENT(?:\s+(?:IS|:|->)|\s*:\s*|\s+)?\s*(IT|COMPLIANCE|ADMINISTRATION|HR|ACCOUNTS)\b",
        text,
    )
    if not explicit_label:
        explicit_label = re.search(r"^(IT|COMPLIANCE|ADMINISTRATION|HR|ACCOUNTS)\b", text)

    if explicit_label:
        label = explicit_label.group(1)
        return {
            "IT": "IT",
            "COMPLIANCE": "Compliance",
            "ADMINISTRATION": "Administration",
            "HR": "HR",
            "ACCOUNTS": "Accounts",
        }.get(label, label)

    if re.search(r"\bIT SUPPORT\b|\bIT DEPARTMENT\b|\bIT TEAM\b", text):
        return "IT"

    for department, keywords in DEPARTMENT_KEYWORDS.items():
        if department == "IT":
            if any(keyword in text for keyword in keywords if keyword != "IT"):
                return department
            continue

        if any(keyword in text for keyword in keywords):
            return department

    return ""


def infer_department_from_route(route_messages, user_text: str) -> str:
    """Scan all route outputs and then fall back to the original user text."""
    text_candidates = []
    for message in route_messages:
        if isinstance(message, str):
            text_candidates.append(message)
        elif hasattr(message, "content") and isinstance(message.content, str):
            text_candidates.append(message.content)

    for candidate in text_candidates:
        department = normalize_department(candidate)
        if department:
            return department

    return normalize_department(user_text)


st.markdown(
    """
    <style>
    :root {
        --ink: #202b28;
        --muted: #68756f;
        --paper: #f5f7f3;
        --line: #dce4dd;
        --green: #176b54;
        --green-soft: #e5f1eb;
        --amber: #d58a32;
    }
    .stApp { background: radial-gradient(ellipse at 75% 0%, #eaf3ed 0, transparent 38%), var(--paper); color: var(--ink); }
    [data-testid="stSidebar"] { background: #edf2ed; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
    .brand-mark {
        display: inline-flex; align-items: center; justify-content: center;
        width: 2rem; height: 2rem; border-radius: 7px; background: var(--green);
        color: white; font-weight: 750; margin-right: .55rem;
    }
    .brand-line { display: flex; align-items: center; color: var(--ink); font-size: 1.08rem; font-weight: 700; }
    .eyebrow { color: var(--green); text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; font-weight: 750; }
    .hero-title { font-size: clamp(1.7rem, 3vw, 2.45rem); line-height: 1.12; font-weight: 720; margin: .45rem 0 .45rem; color: var(--ink); }
    .hero-copy { color: var(--muted); font-size: .97rem; margin-bottom: 1.8rem; }
    .status-row { display: flex; align-items: center; gap: .55rem; color: var(--muted); font-size: .88rem; }
    .status-dot { width: .55rem; height: .55rem; border-radius: 50%; display: inline-block; background: #d58a32; }
    .status-dot.online { background: #27966c; box-shadow: 0 0 0 3px #dcefe5; }
    .agent-label { color: var(--green); font-size: .8rem; font-weight: 700; margin-bottom: .35rem; }
    [data-testid="stChatMessage"] { border: 1px solid var(--line); border-radius: 9px; background: rgba(255,255,255,.82); }
    [data-testid="stChatInput"] { border-color: #b9c9bd; }
    .stButton > button { border-radius: 7px; }
    @media (max-width: 700px) {
        .hero-copy { margin-bottom: 1.1rem; }
        [data-testid="stSidebar"] { min-width: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_agent" not in st.session_state:
    st.session_state.active_agent = "Not assigned"


async def handle_message(user_text: str) -> tuple[str, str]:
    """Route a message, ask the selected department agent, and close the client."""
    model_client = OpenAIChatCompletionClient(model=MODEL, api_key=API_KEY)
    try:
        manager = AssistantAgent(
            name="support_manager",
            model_client=model_client,
            system_message=(
                "You are the customer support manager. Choose the single best "
                "department for the latest user request. Return only one exact "
                "label from this list: IT, Compliance, Administration, HR, Accounts. "
                "Route technical software, hardware, and account-access issues to IT; "
                "security policy, legal, and regulatory issues to Compliance; "
                "facilities, supplies, and office operations to Administration; "
                "employees, payroll, benefits, and hiring to HR; billing, invoices, "
                "expenses, and reimbursements to Accounts. For mixed requests, select "
                "the department that best addresses the main question."
            ),
        )
        history = "\n".join(
            f"{message['role'].capitalize()}: {message['content']}"
            for message in st.session_state.messages[-12:]
        )
        route_result = await manager.run(
            task=f"Conversation so far:\n{history}\n\nLatest user request:\n{user_text}"
        )
        department = infer_department_from_route(route_result.messages, user_text)
        if not department:
            raise RuntimeError("The support manager returned an unknown department.")
        department = department.upper()
        if department not in DEPARTMENTS:
            raise RuntimeError("The support manager returned an unknown department.")

        agent = AssistantAgent(
            name=f"{department.lower()}_agent",
            model_client=model_client,
            system_message=(
                DEPARTMENTS[department]["instructions"]
                + " Use the available tools when they directly support the user request. "
                "Do not invent facts; rely on tool output when appropriate."
            ),
            tools=DEPARTMENT_TOOLS.get(department, []),
        )
        response_result = await agent.run(
            task=(
                f"Conversation so far:\n{history}\n\n"
                f"Latest user request:\n{user_text}\n\n"
                "Respond directly to the latest request."
            )
        )
        response = next(
            (
                message.content.strip()
                for message in reversed(response_result.messages)
                if isinstance(message.content, str) and message.content.strip()
            ),
            "",
        )
        if not response:
            raise RuntimeError("The department agent returned an empty response.")
        return department, response
    finally:
        await model_client.close()


with st.sidebar:
    st.markdown('<div class="brand-line"><span class="brand-mark">N</span>Northstar Support</div>', unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown("### Workspace")
    status_text = "Connected" if API_KEY else "API key required"
    status_class = "online" if API_KEY else ""
    st.markdown(
        f'<div class="status-row"><span class="status-dot {status_class}"></span>{status_text}</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Model: {MODEL}")
    st.markdown(" ")
    st.markdown("**Active department**")
    active_agent_slot = st.empty()
    active_agent_slot.info(st.session_state.active_agent)
    st.markdown(" ")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.active_agent = "Not assigned"
        st.rerun()
    st.markdown(" ")
    st.caption("IT · Compliance · Administration · HR · Accounts")

st.markdown('<div class="eyebrow">Customer care · Internal support</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">How can we help?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-copy">Ask a question and the right support team will take it from here.</div>',
    unsafe_allow_html=True,
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(f'<div class="agent-label">{message["agent"]}</div>', unsafe_allow_html=True)
        st.markdown(message["content"])

if not st.session_state.messages:
    st.caption("Common topics: password access · benefits · office supplies · invoices")

user_text = st.chat_input("Describe what you need help with…")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    if not API_KEY:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "agent": "Setup",
                "content": "Add your OpenAI API key to the local `.env` file, then restart the app.",
            }
        )
    else:
        active_agent_slot.info("Routing request…")
        try:
            with st.spinner("Finding the right support team…"):
                department, answer = asyncio.run(handle_message(user_text))
            st.session_state.active_agent = DEPARTMENTS[department]["name"]
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "agent": DEPARTMENTS[department]["name"],
                    "content": answer,
                }
            )
        except Exception as exc:
            st.session_state.active_agent = "Request failed"
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "agent": "Support system",
                    "content": (
                        "The request failed. Details: "
                        f"{exc}. Check your API key, model availability, and network connection."
                    ),
                }
            )
    st.rerun()