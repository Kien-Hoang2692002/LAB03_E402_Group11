import streamlit as st
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.core.openai_provider import OpenAIProvider
from chatbot_baseline import BaseChatbot
import statistics

st.set_page_config(
    page_title="Shopping Deal Assistant",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Shopping Deal Assistant")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Provider selection
    provider = st.selectbox(
        "LLM Provider:",
        ("Gemini (Fast, Free tier)", "OpenAI (GPT-4o)")
    )
    provider_key = "gemini" if "Gemini" in provider else "openai"
    
    # Mode selection
    mode = st.radio(
        "Choose Mode:",
        ("🤖 Agent (Real-time API)", "💬 Chatbot (Training Data)")
    )
    
    if mode == "🤖 Agent (Real-time API)":
        max_steps = st.slider("Max Steps:", 3, 10, 5)
    else:
        max_steps = None
    
    if st.button("🗑️ Clear Current Chat"):
        if mode == "🤖 Agent (Real-time API)":
            st.session_state.agent_messages = []
            st.session_state.agent_metrics = []
        else:
            st.session_state.chatbot_messages = []
            st.session_state.chatbot_metrics = []
        st.rerun()

# Initialize session state
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []
if "agent_metrics" not in st.session_state:
    st.session_state.agent_metrics = []
if "chatbot_messages" not in st.session_state:
    st.session_state.chatbot_messages = []
if "chatbot_metrics" not in st.session_state:
    st.session_state.chatbot_metrics = []

# Select current messages and metrics
if mode == "🤖 Agent (Real-time API)":
    current_messages = st.session_state.agent_messages
    current_metrics = st.session_state.agent_metrics
    current_role = "agent"
    current_avatar = "🤖"
else:
    current_messages = st.session_state.chatbot_messages
    current_metrics = st.session_state.chatbot_metrics
    current_role = "chatbot"
    current_avatar = "💬"

# Display chat history
for message in current_messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else current_avatar):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    # Add user message
    current_messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Process response
    with st.chat_message(current_role, avatar=current_avatar):
        with st.spinner("Thinking..."):
            try:
                if mode == "🤖 Agent (Real-time API)":
                    # Select provider for agent
                    if provider_key == "gemini":
                        llm = GeminiProvider()
                    else:
                        llm = OpenAIProvider()
                    
                    agent = ReActAgent(llm=llm, max_steps=max_steps)
                    result = agent.run(prompt)
                    response = result["response"]
                    latency_ms = result["latency_ms"]
                    tokens = result["tokens_used"]
                    cost = 0  # Agent cost calculation
                else:
                    # Chatbot with selected provider
                    chatbot = BaseChatbot(provider=provider_key)
                    result = chatbot.chat(prompt)
                    response = result["response"]
                    latency_ms = result["latency_ms"]
                    tokens = result["tokens_used"]
                    cost = result["cost"]
                
                st.markdown(response)
                current_messages.append({
                    "role": current_role,
                    "content": response
                })
                
                # Store metrics
                current_metrics.append({
                    "latency_ms": latency_ms,
                    "tokens": tokens,
                    "cost": cost
                })
            
            except Exception as e:
                error_msg = f"❌ Lỗi: {str(e)}"
                st.error(error_msg)
                current_messages.append({
                    "role": current_role,
                    "content": error_msg
                })

# ===== TELEMETRY & PERFORMANCE DASHBOARD =====
if current_metrics:
    st.markdown("---")
    st.markdown("### 📊 Performance Dashboard")
    
    latencies = [m["latency_ms"] for m in current_metrics]
    tokens_list = [m["tokens"] for m in current_metrics]
    costs = [m["cost"] for m in current_metrics]
    
    p50_latency = statistics.median(latencies)
    p99_latency = latencies[int(len(latencies) * 0.99)] if len(latencies) > 1 else max(latencies)
    
    avg_latency = statistics.mean(latencies)
    avg_tokens = statistics.mean(tokens_list)
    total_cost = sum(costs)
    total_requests = len(current_metrics)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Requests", total_requests)
    
    with col2:
        st.metric("⏱️ Avg Latency", f"{avg_latency:.0f}ms")
    
    with col3:
        st.metric("📝 Avg Tokens", f"{avg_tokens:.0f}")
    
    with col4:
        st.metric("💰 Total Cost", f"${total_cost:.6f}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("⚡ P50 Latency", f"{p50_latency:.0f}ms")
    
    with col2:
        st.metric("🔴 P99 Latency", f"{p99_latency:.0f}ms")
    
    with col3:
        st.metric("📈 Min Latency", f"{min(latencies):.0f}ms")
    
    with col4:
        st.metric("📉 Max Latency", f"{max(latencies):.0f}ms")