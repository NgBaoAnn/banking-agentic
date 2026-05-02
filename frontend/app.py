"""
Streamlit Frontend for the Banking AI-Agent.
Provides a chat interface to interact with the backend pipeline.
"""

import os
import json
import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# ── Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Banking AI-Agent",
    page_icon="🏦",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
    }
    .node-card {
        background-color: #1e1e2e;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #89b4fa;
    }
    .priority-high { border-left-color: #f38ba8 !important; }
    .priority-medium { border-left-color: #fab387 !important; }
    .priority-low { border-left-color: #a6e3a1 !important; }
    .action-reply { color: #a6e3a1; }
    .action-escalate { color: #f38ba8; }
    .action-ask_more { color: #fab387; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────
st.markdown("# 🏦 Banking AI-Agent")
st.markdown("*AI-powered customer support pipeline with intent detection, "
            "policy retrieval, and smart routing*")
st.divider()

# ── Sidebar — Settings ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    api_url = st.text_input("Backend API URL", value=API_BASE_URL)
    st.divider()
    st.header("📋 Sample Messages")
    samples = [
        "I tried to send money to my friend but the transfer failed.",
        "My account has been blocked and I cannot access my funds!",
        "I lost my card yesterday and I need a replacement.",
        "What is the current exchange rate for USD to EUR?",
        "I was charged twice for the same transaction. I need a refund.",
        "I applied for a new card two weeks ago but haven't received it.",
        "I noticed transactions I did not make. Someone stole my info!",
        "I tried to top up my account but it failed.",
    ]
    for sample in samples:
        if st.button(sample[:60] + "...", key=sample):
            st.session_state["input_message"] = sample

# ── Main Chat Interface ────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💬 Customer Message")
    default_msg = st.session_state.get("input_message", "")
    message = st.text_area(
        "Enter your banking question:",
        value=default_msg,
        height=120,
        placeholder="Type your banking-related question here...",
    )

    send_btn = st.button("🚀 Send to AI Agent", type="primary", use_container_width=True)

if send_btn and message.strip():
    with st.spinner("🔄 Processing through AI pipeline..."):
        try:
            resp = requests.post(
                f"{api_url}/api/chat",
                json={"message": message},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Is the API server running?")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.stop()

    # ── Display Results ─────────────────────────────────────────
    trace = data.get("trace", {})
    action = data.get("action", "unknown")

    with col2:
        st.subheader("📊 Pipeline Results")

        # Final action badge
        action_emoji = {"reply": "✅", "ask_more": "❓", "escalate": "🚨"}.get(action, "❔")
        action_color = {"reply": "green", "ask_more": "orange", "escalate": "red"}.get(action, "gray")
        st.markdown(f"### {action_emoji} Final Action: :{action_color}[**{action.upper()}**]")

    # ── Workflow Trace ──────────────────────────────────────────
    st.divider()
    st.subheader("🔍 Workflow Trace")

    trace_cols = st.columns(3)

    # Node 1: Intent
    with trace_cols[0]:
        intent = trace.get("intent", {})
        st.markdown("#### 🎯 Step 1: Intent Detection")
        st.metric("Intent", intent.get("intent", "N/A"))
        st.metric("Confidence", f"{intent.get('confidence', 0):.1%}")
        st.caption(intent.get("reason", ""))

    # Node 2: Priority
    with trace_cols[1]:
        priority = trace.get("priority", {})
        level = priority.get("level", "N/A")
        level_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
        st.markdown("#### ⚡ Step 2: Priority")
        st.metric("Level", f"{level_emoji} {level.upper()}")
        for factor in priority.get("factors", []):
            st.caption(f"• {factor}")

    # Node 3: Policy
    with trace_cols[2]:
        policy = trace.get("policy", {})
        st.markdown("#### 📜 Step 3: Policy Retrieval")
        st.metric("Policy", policy.get("policy_title", "N/A"))
        with st.expander("View Policy Details"):
            st.write(policy.get("policy_text", ""))
            st.write(f"**Resolution:** {policy.get('typical_resolution', '')}")

    trace_cols2 = st.columns(3)

    # Node 4: Draft
    with trace_cols2[0]:
        draft = trace.get("draft", {})
        st.markdown("#### ✍️ Step 4: Draft Response")
        with st.expander("View Draft", expanded=True):
            st.write(draft.get("reply", "No draft generated"))
        if draft.get("missing_info"):
            st.warning("Missing info: " + ", ".join(draft["missing_info"]))

    # Node 5: Validation
    with trace_cols2[1]:
        validation = trace.get("validation", {})
        st.markdown("#### ✅ Step 5: Validation")
        valid_status = "✅ PASSED" if validation.get("is_valid") else "❌ FAILED"
        st.metric("Status", valid_status)
        st.metric("Score", f"{validation.get('score', 0):.0%}")
        for issue in validation.get("issues", []):
            st.error(f"• {issue}")

    # Node 6: Routing
    with trace_cols2[2]:
        routing = trace.get("routing", {})
        st.markdown("#### 🔀 Step 6: Routing Decision")
        st.metric("Action", routing.get("action", "N/A").upper())
        st.caption(routing.get("reason", ""))

    # ── Final Response ──────────────────────────────────────────
    st.divider()
    st.subheader("💬 Final Response to Customer")

    if action == "escalate":
        st.error(data.get("final_response", ""))
    elif action == "ask_more":
        st.warning(data.get("final_response", ""))
    else:
        st.success(data.get("final_response", ""))

elif send_btn:
    st.warning("Please enter a message first.")
