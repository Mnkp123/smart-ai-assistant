import streamlit as st
import json
from chat_engine import get_ai_response
from rag_system import RAGSystem
from lead_manager import load_leads, save_lead, classify_lead, generate_followup_email
from agents import PlannerAgent, ExecutorAgent, ValidatorAgent
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME

st.set_page_config(
    page_title="Smart AI Business Assistant",
    page_icon="🤖",
    layout="wide"
)

@st.cache_resource
def init_systems():
    return RAGSystem(), PlannerAgent(), ExecutorAgent(), ValidatorAgent()

rag, planner, executor, validator = init_systems()

st.sidebar.title("🤖 AI Business Assistant")
st.sidebar.markdown("---")
page = st.sidebar.selectbox("Navigation", [
    "💬 Chat Assistant",
    "👥 Lead Management",
    "📄 Document Upload",
    "⚡ Automations",
    "📊 Dashboard",
    "📝 Logs"
])

# ===== CHAT PAGE =====
if page == "💬 Chat Assistant":
    st.title("💬 AI Business Assistant")
    st.caption("Powered by Groq + RAG + Multi-Agent System")

    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Type your message..."):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("🤔 Thinking..."):
            plan = planner.plan(prompt)
            response, context = executor.execute(
                plan, prompt, rag,
                st.session_state.conversation_history
            )
            is_valid, reason = validator.validate(response, context)

        with st.chat_message("assistant"):
            st.write(response)
            if context:
                with st.expander("📚 Source Context Used"):
                    st.write(context[:400] + "...")
            if not is_valid:
                st.warning(f"⚠️ {reason}")

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        st.session_state.conversation_history.append({"role": "assistant", "content": response})

        # Auto lead capture
        buy_keywords = ['buy', 'price', 'cost', 'purchase', 'interested',
                       'need', 'want', 'quote', 'khareedna', 'chahiye', 'budget']
        
        if any(word in prompt.lower() for word in buy_keywords):
            conv_text = "\n".join([
                f"{m['role']}: {m['content']}"
                for m in st.session_state.messages[-6:]
            ])
            with st.spinner("🎯 Detecting lead..."):
                lead_data = classify_lead(conv_text)
                save_lead(lead_data)
            temp = lead_data['temperature'].upper()
            name = lead_data.get('name', 'Unknown')
            st.success(f"✅ Lead captured! **{name}** → Temperature: **{temp}**")

# ===== LEADS PAGE =====
elif page == "👥 Lead Management":
    st.title("👥 Lead Management")
    leads = load_leads()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Total", len(leads))
    col2.metric("🔥 Hot", len([l for l in leads if l.get('temperature') == 'hot']))
    col3.metric("🌡️ Warm", len([l for l in leads if l.get('temperature') == 'warm']))
    col4.metric("❄️ Cold", len([l for l in leads if l.get('temperature') == 'cold']))

    st.markdown("---")
    filter_temp = st.selectbox("Filter", ["All", "hot", "warm", "cold"])
    filtered = leads if filter_temp == "All" else [
        l for l in leads if l.get('temperature') == filter_temp
    ]

    if not filtered:
        st.info("Koi leads nahi hain abhi. Chat mein conversation karo!")

    for lead in reversed(filtered):
        icon = {"hot": "🔥", "warm": "🌡️", "cold": "❄️"}.get(lead.get('temperature'), "❓")
        with st.expander(f"{icon} {lead.get('name', 'Unknown')} — {lead.get('timestamp', '')}"):
            c1, c2 = st.columns(2)
            c1.write(f"**Email:** {lead.get('email', 'N/A')}")
            c1.write(f"**Phone:** {lead.get('phone', 'N/A')}")
            c2.write(f"**Requirements:** {lead.get('requirements', 'N/A')}")
            c2.write(f"**Reason:** {lead.get('reason', 'N/A')}")
            if st.button("📧 Generate Follow-up Email", key=f"fu_{lead.get('id')}"):
                with st.spinner("Writing email..."):
                    email = generate_followup_email(lead)
                st.text_area("Email:", email, height=200)

# ===== DOCUMENTS PAGE =====
elif page == "📄 Document Upload":
    st.title("📄 Document Management")
    st.write("Upload business documents — AI will use these to answer questions")

    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf', 'md'])
    if uploaded_file:
        if st.button("⚙️ Process Document"):
            with st.spinner("Processing..."):
                text = uploaded_file.read().decode('utf-8', errors='ignore')
                chunks = rag.add_document(text, uploaded_file.name)
            st.success(f"✅ Done! Created {chunks} searchable chunks.")

    st.markdown("---")
    st.subheader("📚 Uploaded Documents")
    docs = rag.get_all_docs()
    if docs:
        for doc in docs:
            st.write(f"📄 {doc}")
    else:
        st.info("No documents yet. Upload one above!")

# ===== AUTOMATIONS PAGE =====
elif page == "⚡ Automations":
    st.title("⚡ Workflow Automations")
    client_groq = Groq(api_key=GROQ_API_KEY)

    tab1, tab2, tab3 = st.tabs([
        "📧 Email Summarizer",
        "📊 Lead Report",
        "💌 Bulk Follow-up"
    ])

    with tab1:
        st.subheader("Email Summarizer")
        st.caption("Paste multiple emails, get a clean summary")
        emails_input = st.text_area(
            "Paste emails here:",
            height=200,
            placeholder="Email 1...\n---\nEmail 2..."
        )
        if st.button("✨ Summarize"):
            if emails_input:
                with st.spinner("Summarizing..."):
                    res = client_groq.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{
                            "role": "user",
                            "content": f"Summarize these emails clearly in bullet points:\n{emails_input}"
                        }],
                        max_tokens=500
                    )
                st.success("Done!")
                st.write(res.choices[0].message.content)
            else:
                st.warning("Please paste some emails first!")

    with tab2:
        st.subheader("Daily Lead Report")
        if st.button("📈 Generate Report"):
            leads = load_leads()
            if leads:
                with st.spinner("Analyzing..."):
                    res = client_groq.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{
                            "role": "user",
                            "content": f"Analyze these leads and give business insights:\n{json.dumps(leads[-10:], indent=2)}"
                        }],
                        max_tokens=500
                    ).choices[0].message.content
                col1, col2, col3 = st.columns(3)
                col1.metric("Total", len(leads))
                col2.metric("Hot", len([l for l in leads if l.get('temperature') == 'hot']))
                col3.metric("Warm", len([l for l in leads if l.get('temperature') == 'warm']))
                st.markdown("### AI Analysis")
                st.write(res)
            else:
                st.info("No leads yet to analyze!")

    with tab3:
        st.subheader("Bulk Follow-up Generator")
        leads = load_leads()
        hot_leads = [l for l in leads if l.get('temperature') == 'hot']
        st.write(f"🔥 {len(hot_leads)} hot leads found")
        if hot_leads and st.button("Generate All Follow-ups"):
            for lead in hot_leads[:5]:
                with st.expander(f"Email for {lead.get('name', 'Unknown')}"):
                    with st.spinner("Writing..."):
                        email = generate_followup_email(lead)
                    st.write(email)
        elif not hot_leads:
            st.info("No hot leads yet!")

# ===== DASHBOARD PAGE =====
elif page == "📊 Dashboard":
    st.title("📊 Analytics Dashboard")
    leads = load_leads()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Leads", len(leads))
    col2.metric("🔥 Hot", len([l for l in leads if l.get('temperature') == 'hot']))
    col3.metric("🌡️ Warm", len([l for l in leads if l.get('temperature') == 'warm']))
    col4.metric("💬 Messages", len(st.session_state.get('messages', [])))

    if leads:
        import pandas as pd
        df = pd.DataFrame(leads)
        st.markdown("---")
        st.subheader("Lead Temperature Distribution")
        temp_counts = df['temperature'].value_counts()
        st.bar_chart(temp_counts)

        st.subheader("📋 All Leads")
        show_cols = [c for c in ['name', 'email', 'temperature', 'requirements', 'timestamp'] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True)
    else:
        st.info("Koi data nahi hai abhi. Pehle chat karo aur leads capture karo!")

# ===== LOGS PAGE =====
elif page == "📝 Logs":
    st.title("📝 System Logs")

    st.subheader("💬 Conversation Log")
    messages = st.session_state.get('messages', [])
    if messages:
        for msg in messages:
            icon = "👤" if msg['role'] == 'user' else "🤖"
            st.write(f"{icon} **{msg['role'].title()}:** {msg['content'][:200]}")
    else:
        st.info("No conversations yet")

    st.markdown("---")
    st.subheader("👥 Recent Lead Activity")
    leads = load_leads()
    if leads:
        for lead in reversed(leads[-5:]):
            icon = {"hot": "🔥", "warm": "🌡️", "cold": "❄️"}.get(lead.get('temperature'), "❓")
            st.write(f"{icon} [{lead.get('timestamp')}] {lead.get('name')} — {lead.get('temperature', '').upper()}")
    else:
        st.info("No leads yet")