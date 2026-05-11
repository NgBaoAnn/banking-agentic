import os
import json
import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# ── Page Config ───────────────────────
st.set_page_config(
    page_title="Banking AI agent",
    page_icon=":material/account_balance:",
    layout="wide",
)

# ── Header 
st.title("Banking AI agent")
st.caption("AI-powered customer support pipeline with intent detection, policy retrieval, and smart routing")

# ── Sidebar — Settings ────────────────
with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("Backend API URL", value=API_BASE_URL)
    
    st.header("Test Cases")
    samples = [
        "[REPLY] What is the exchange rate for USD to EUR?",
        "[ASK_MORE] I tried to send money but the transfer failed.",
        "[ASK_MORE] I applied for a new card but haven't received it.",
        "[ESCALATE] I lost my card yesterday and I need a replacement.",
        "[ESCALATE] My card was compromised and there are charges I didn't make!",
    ]
    for sample in samples:
        # Hide prefix when putting into chat box
        if st.button(sample, key=sample):
            st.session_state["input_message"] = sample.split("] ")[1]

# ── Main Chat Interface ──────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Customer message")
    default_msg = st.session_state.get("input_message", "")
    message = st.text_area(
        "Enter your banking question:",
        value=default_msg,
        height=120,
        placeholder="Type your banking-related question here...",
        label_visibility="collapsed"
    )

    send_btn = st.button("Send to AI agent", type="primary", use_container_width=True)

if send_btn and message.strip():
    with st.spinner("Processing through AI pipeline..."):
        try:
            resp = requests.post(
                f"{api_url}/api/chat",
                json={"message": message},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Is the API server running?")
            st.stop()
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
            st.stop()

    # ── Display Results ───────────
    trace = data.get("trace", {})
    action = data.get("action", "unknown")

    with col2:
        st.subheader("Final resolution")
        
        # Final action badge
        action_color = {"reply": "green", "ask_more": "orange", "escalate": "red"}.get(action, "gray")
        st.markdown(f"**Action required:** :{action_color}-badge[{action.upper()}]")
        
        if action == "escalate":
            st.error(data.get("final_response", ""))
        elif action == "ask_more":
            st.warning(data.get("final_response", ""))
        else:
            st.success(data.get("final_response", ""))

    # ── Workflow Trace ────────────
    st.subheader("Workflow trace")

    trace_cols = st.columns(3)

    # Node 1: Intent
    with trace_cols[0].container(border=True):
        intent = trace.get("intent", {})
        st.markdown("**Step 1: Intent detection**")
        st.metric("Intent", intent.get("intent", "N/A"))
        st.metric("Confidence", f"{intent.get('confidence', 0):.1%}")
        st.caption(intent.get("reason", ""))

    # Node 2: Priority
    with trace_cols[1].container(border=True):
        priority = trace.get("priority", {})
        level = priority.get("level", "N/A")
        
        # Determine badge color based on priority
        level_color = {"high": "red", "medium": "orange", "low": "green"}.get(level.lower(), "gray")
        st.markdown(f"**Step 2: Priority level**")
        st.markdown(f":{level_color}-badge[{level.upper()}]")
        for factor in priority.get("factors", []):
            st.caption(f"• {factor}")

    # Node 3: Policy
    with trace_cols[2].container(border=True):
        policy = trace.get("policy", {})
        st.markdown("**Step 3: Policy retrieval**")
        st.metric("Policy", policy.get("policy_title", "N/A"))
        with st.expander("View policy details"):
            st.write(policy.get("policy_text", ""))
            st.write(f"**Resolution:** {policy.get('typical_resolution', '')}")

    trace_cols2 = st.columns(3)

    # Node 4: Draft
    with trace_cols2[0].container(border=True):
        draft = trace.get("draft", {})
        st.markdown("**Step 4: Draft response**")
        with st.expander("View draft", expanded=True):
            st.write(draft.get("reply", "No draft generated"))
        if draft.get("missing_info"):
            st.warning("Missing info: " + ", ".join(draft["missing_info"]))

    # Node 5: Validation
    with trace_cols2[1].container(border=True):
        validation = trace.get("validation", {})
        st.markdown("**Step 5: Validation**")
        is_valid = validation.get("is_valid", False)
        valid_status = "PASSED" if is_valid else "FAILED"
        valid_color = "green" if is_valid else "red"
        st.markdown(f":{valid_color}-badge[{valid_status}]")
        st.metric("Score", f"{validation.get('score', 0):.0%}")
        for issue in validation.get("issues", []):
            st.error(f"• {issue}")

    # Node 6: Routing
    with trace_cols2[2].container(border=True):
        routing = trace.get("routing", {})
        st.markdown("**Step 6: Routing decision**")
        route_action = routing.get("action", "N/A").upper()
        st.metric("Action", route_action)
        st.caption(routing.get("reason", ""))

elif send_btn:
    st.warning("Please enter a message first.")
