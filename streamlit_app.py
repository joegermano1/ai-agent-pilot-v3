import streamlit as st
from datetime import datetime
import json

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Agent Pilot",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Session State Initialization
# -----------------------------
if "step" not in st.session_state:
    st.session_state.step = "preflight"

if "agent_data" not in st.session_state:
    st.session_state.agent_data = {
        "aim": "",
        "dod": "",
        "soul": "",
        "identity": "",
        "user": "",
        "equip_notes": "",
        "manager_prompt": "",
        "specialists": [],
        "trust_stage": 1,
        "schedule": "Every morning at 9:00 AM",
        "guardrails": ""
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# System Prompt for Co-Pilot
# -----------------------------
SYSTEM_PROMPT = """You are the AI Agent Pilot Coach inside the AI Agent Pilot app.

Your only job is to guide the user through building their own AI agent using Dan Martell’s AGENT framework. You never build the agent for them. You never skip steps. You never do the work yourself.

Core rules you must follow at all times:
- Enforce the Rule of R first: the task must be Repetitive, Rules-based, and deliver a clear Return on time. If it fails any of the three, stop the user and suggest using regular chat instead.
- Follow the exact order: A → G → E → N → T.
- When generating identity files, only do so after the user has answered your clarifying questions.
- Always remind the user: “One agent, one lane.”
- Use the exact prompt templates from the video as the foundation and help the user customize them.
- Stay encouraging but firm. Keep the user moving forward without doing the thinking for them.
- Speak in a clear, direct, professional coaching tone. Short paragraphs. No fluff.

When the user is on a specific step, stay focused only on that step unless they explicitly ask to go back.

Key prompts you reference and help customize:
- Identity files: “I want to build an AI agent that runs my [task]. Create its three identity files: a SOUL file, an IDENTITY file, and a USER file (about me). Ask me any questions you need to fill these in accurately, then write all three.”
- Manager agent: “You are my Manager agent. You never do any task yourself. When a job comes in, your only move is to spin up a dedicated sub-agent for that one job, hand it the task, and let it run. One agent, one lane…”
- Specialist: “Your one job is [specific lane] — nothing else. You never step outside [that lane].”

Always end your responses by telling the user exactly what to do next.
"""

# -----------------------------
# Helper: Call AI (OpenAI-compatible)
# -----------------------------
def call_ai(user_message: str, system: str = SYSTEM_PROMPT) -> str:
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=st.secrets.get("OPENAI_API_KEY") or st.secrets.get("GROK_API_KEY"),
            # base_url="https://api.x.ai/v1"   # uncomment if using Grok
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI call failed. Check your API key in secrets. Error: {str(e)}"

# -----------------------------
# Sidebar
# -----------------------------
steps_list = [
    ("preflight", "1. Pre-Flight (Rule of R)"),
    ("aim", "2. A – Aim"),
    ("identity", "3. G – Identity"),
    ("equip", "4. E – Equip"),
    ("narrow", "5. N – Narrow Scope"),
    ("trust", "6. T – Trust"),
    ("export", "7. Export")
]

with st.sidebar:
    st.title("✈️ AI Agent Pilot")
    st.caption("Build real AI agents step-by-step")
    st.divider()
    
    st.subheader("Progress")
    for key, label in steps_list:
        if st.session_state.step == key:
            st.markdown(f"**→ {label}**")
        else:
            st.markdown(label)
    
    st.divider()
    if st.button("Reset Agent", type="secondary"):
        st.session_state.step = "preflight"
        st.session_state.agent_data = {
            "aim": "", "dod": "", "soul": "", "identity": "", "user": "",
            "equip_notes": "", "manager_prompt": "", "specialists": [],
            "trust_stage": 1, "schedule": "Every morning at 9:00 AM", "guardrails": ""
        }
        st.session_state.messages = []
        st.rerun()

# -----------------------------
# Main Content
# -----------------------------
st.title("AI Agent Pilot")
st.caption("Follow the AGENT framework to build your first real AI agent")

# ========== PRE-FLIGHT ==========
if st.session_state.step == "preflight":
    st.header("Pre-Flight Check — Rule of R")
    st.write("Only build an agent if the task passes all three tests.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        r1 = st.radio("Is it **Repetitive**?", ["Yes", "No"], key="r1")
    with col2:
        r2 = st.radio("Is it **Rules-based**?", ["Yes", "No"], key="r2")
    with col3:
        r3 = st.radio("Strong **Return on time**?", ["Yes", "No"], key="r3")
    
    if st.button("Continue →", type="primary"):
        if r1 == "Yes" and r2 == "Yes" and r3 == "Yes":
            st.session_state.step = "aim"
            st.rerun()
        else:
            st.error("This task does not pass the Rule of R. Use regular AI chat instead of building an agent.")

# ========== A – AIM ==========
elif st.session_state.step == "aim":
    st.header("A – Aim for a Specific Outcome")
    st.write("Define exactly what success looks like.")
    
    aim = st.text_area("What specific outcome do you want this agent to achieve?", 
                       value=st.session_state.agent_data["aim"], height=100)
    dod = st.text_area("Definition of Done (be very specific)", 
                       value=st.session_state.agent_data["dod"], height=100,
                       placeholder="Example: Every morning by 9:00 AM my inbox is empty and replies are drafted in my exact voice.")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = "preflight"
            st.rerun()
    with col2:
        if st.button("Save & Continue →", type="primary"):
            if aim.strip() and dod.strip():
                st.session_state.agent_data["aim"] = aim
                st.session_state.agent_data["dod"] = dod
                st.session_state.step = "identity"
                st.rerun()
            else:
                st.warning("Please fill in both fields.")

# ========== G – IDENTITY ==========
elif st.session_state.step == "identity":
    st.header("G – Give It an Identity")
    st.write("Create the three core files: **SOUL**, **IDENTITY**, and **USER**.")
    
    st.info("Tip: Click the button below and let the Co-Pilot ask you questions, then generate the files.")
    
    if st.button("Ask Co-Pilot to generate Identity files", type="primary"):
        prompt = f"""I want to build an AI agent that achieves this outcome: {st.session_state.agent_data['aim']}

Definition of Done: {st.session_state.agent_data['dod']}

Create its three identity files: a SOUL file, an IDENTITY file, and a USER file (about me). 
Ask me any questions you need to fill these in accurately, then write all three.
"""
        with st.spinner("Co-Pilot is thinking..."):
            reply = call_ai(prompt)
            st.session_state.messages.append({"role": "assistant", "content": reply})
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    st.subheader("Edit the files directly")
    soul = st.text_area("SOUL (personality & behavior)", value=st.session_state.agent_data["soul"], height=150)
    identity = st.text_area("IDENTITY (role & DNA)", value=st.session_state.agent_data["identity"], height=150)
    user = st.text_area("USER (context about you)", value=st.session_state.agent_data["user"], height=150)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = "aim"
            st.rerun()
    with col2:
        if st.button("Save & Continue →", type="primary"):
            st.session_state.agent_data["soul"] = soul
            st.session_state.agent_data["identity"] = identity
            st.session_state.agent_data["user"] = user
            st.session_state.step = "equip"
            st.rerun()

# ========== E – EQUIP ==========
# ========== E – EQUIP ==========
elif st.session_state.step == "equip":
    st.header("E – Equip It")
    st.write("Give the agent the context, examples, and tools it needs.")

    st.subheader("Upload Reference Files")
    st.caption("Upload examples of your writing, past emails, process docs, brand voice guides, or guardrail documents.")

    uploaded_files = st.file_uploader(
        "Upload files (PDF, TXT, MD, DOCX, etc.)",
        accept_multiple_files=True,
        type=["txt", "md", "pdf", "docx", "csv"]
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully.")
        file_names = [f.name for f in uploaded_files]
        st.write("Uploaded files:", ", ".join(file_names))

        # Save file names into session state
        st.session_state.agent_data["uploaded_files"] = file_names
    else:
        st.session_state.agent_data["uploaded_files"] = []

    st.markdown("---")

    equip = st.text_area(
        "Additional context, style notes, tools, and process instructions",
        value=st.session_state.agent_data.get("equip_notes", ""),
        height=200,
        placeholder="Example: Use a professional but friendly tone. Never make promises about pricing. Always check the calendar before suggesting meeting times..."
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = "identity"
            st.rerun()
    with col2:
        if st.button("Save & Continue →", type="primary"):
            st.session_state.agent_data["equip_notes"] = equip
            st.session_state.step = "narrow"
            st.rerun()

# ========== N – NARROW ==========
elif st.session_state.step == "narrow":
    st.header("N – Narrow the Scope")
    st.write("One agent, one lane. Create a Manager + specialist sub-agents.")
    
    manager = st.text_area(
        "Manager Agent Prompt",
        value=st.session_state.agent_data.get("manager_prompt") or 
              "You are my Manager agent. You never do any task yourself. When a job comes in, your only move is to spin up a dedicated sub-agent for that one job, hand it the task, and let it run. One agent, one lane. If a job touches on multiple areas, split it into separate sub-agents, one per area. You coordinate and report back to me.",
        height=120
    )
    
    st.subheader("Specialist Sub-Agents")
    num_specs = st.number_input("How many specialists?", min_value=1, max_value=6, value=2)
    
    specialists = []
    for i in range(num_specs):
        name = st.text_input(f"Specialist {i+1} name", key=f"spec_name_{i}", value=f"Specialist {i+1}")
        lane = st.text_area(f"Specialist {i+1} job (one lane only)", key=f"spec_lane_{i}", height=80,
                            placeholder="Your one job is [specific task] — nothing else. You never step outside that lane.")
        specialists.append({"name": name, "lane": lane})
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = "equip"
            st.rerun()
    with col2:
        if st.button("Save & Continue →", type="primary"):
            st.session_state.agent_data["manager_prompt"] = manager
            st.session_state.agent_data["specialists"] = specialists
            st.session_state.step = "trust"
            st.rerun()

# ========== T – TRUST ==========
elif st.session_state.step == "trust":
    st.header("T – Trust in Stages")
    st.write("Start with oversight and gradually increase autonomy.")
    
    stage = st.select_slider(
        "Current Trust Stage",
        options=[1, 2, 3, 4],
        value=st.session_state.agent_data["trust_stage"],
        format_func=lambda x: {
            1: "1 – Approve everything",
            2: "2 – Review drafts only",
            3: "3 – Auto-run + daily summary",
            4: "4 – Fully trusted with guardrails"
        }[x]
    )
    
    schedule = st.text_input("Run Schedule", value=st.session_state.agent_data["schedule"])
    guardrails = st.text_area("Hard Guardrails / Stop Rules", value=st.session_state.agent_data["guardrails"], height=100)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.step = "narrow"
            st.rerun()
    with col2:
        if st.button("Save & Continue to Export →", type="primary"):
            st.session_state.agent_data["trust_stage"] = stage
            st.session_state.agent_data["schedule"] = schedule
            st.session_state.agent_data["guardrails"] = guardrails
            st.session_state.step = "export"
            st.rerun()

# ========== EXPORT ==========
# ========== EXPORT ==========
elif st.session_state.step == "export":
    st.header("Export Your Agent Package")
    st.success("Your agent is ready!")

    data = st.session_state.agent_data

    # Build markdown
    md = f"""# AI Agent Pilot – Export Package
**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Framework:** Dan Martell AGENT Method

## 1. Aim / Definition of Done
**Outcome:** {data['aim']}

**Definition of Done:**  
{data['dod']}

## 2. Identity Files

### SOUL
{data['soul'] or "_Not filled yet_"}

### IDENTITY
{data['identity'] or "_Not filled yet_"}

### USER
{data['user'] or "_Not filled yet_"}

## 3. Manager Agent Prompt
{data['manager_prompt']}

## 4. Specialist Sub-Agents
"""
    for i, spec in enumerate(data.get("specialists", []), 1):
        md += f"""
### Specialist {i}: {spec.get('name', 'Unnamed')}
{spec.get('lane', '')}
"""

    md += f"""
## 5. Equip / Context & Tools
{data.get('equip_notes') or "_None provided_"}

**Uploaded Reference Files:** {', '.join(data.get('uploaded_files', [])) or "None"}

## 6. Trust Stage & Schedule
- **Current Stage:** {data['trust_stage']}
- **Schedule:** {data['schedule']}
- **Guardrails:** {data['guardrails'] or "None"}

---

## How to Start Your Agent

### Option 1: Claude (Recommended)
1. Go to [claude.ai](https://claude.ai)
2. Create a new Project
3. Upload any reference files you have
4. Paste the **SOUL + IDENTITY + USER** files into the Project instructions
5. Paste the Manager prompt as the main system prompt
6. Create separate chats or projects for each Specialist if needed
7. Start with Trust Stage 1 (approve everything)

### Option 2: Custom GPT (ChatGPT)
1. Go to ChatGPT → Create a GPT
2. Paste the Identity files and Manager prompt into the Instructions
3. Upload your reference files
4. Save and start testing

### Option 3: Grok or other platforms
Copy the prompts into the system prompt / custom instructions area and attach your files.

**Important:**  
Always start at Trust Stage 1. Only increase autonomy after the agent has proven it follows your style and rules consistently.
"""

    st.download_button(
        label="Download Agent Package (.md)",
        data=md,
        file_name=f"agent_package_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown",
        type="primary"
    )

    st.subheader("Full Package Preview")
    st.code(md, language="markdown")

    st.markdown("---")
    st.subheader("Next Steps After Export")
    st.markdown("""
1. Download the package above  
2. Choose your platform (Claude Projects is currently the strongest option)  
3. Paste the identity files and prompts  
4. Upload your reference documents  
5. Run real tasks and stay in Trust Stage 1 at the beginning  
6. Improve the prompts based on what the agent gets wrong
    """)

    if st.button("← Back to Trust"):
        st.session_state.step = "trust"
        st.rerun()
