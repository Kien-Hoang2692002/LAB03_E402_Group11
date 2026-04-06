import streamlit as st
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.core.openai_provider import OpenAIProvider
<<<<<<< HEAD
from chatbot_baseline import BaseChatbot
import statistics
=======
from chatbot_baseline import OpenAIChatbot, GeminiChatbot
from src.telemetry.logger import logger
>>>>>>> 796463936eb27059360248792004d25343f046ac


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Shopping Deal Assistant",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Shopping Deal Assistant")


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Settings")
<<<<<<< HEAD
    
    # Provider selection
    provider = st.selectbox(
        "LLM Provider:",
        ("Gemini (Fast, Free tier)", "OpenAI (GPT-4o)")
    )
    provider_key = "gemini" if "Gemini" in provider else "openai"
    
    # Mode selection
=======

>>>>>>> 796463936eb27059360248792004d25343f046ac
    mode = st.radio(
        "Choose Mode:",
        ("🤖 Agent (Real-time API)", "💬 Chatbot (Training Data)")
    )

    provider_choice = st.radio(
        "LLM Provider:",
        ("Auto (Gemini → OpenAI)", "Gemini", "OpenAI")
    )

    if mode == "🤖 Agent (Real-time API)":
        max_steps = st.slider("Max Steps:", 3, 10, 5)
        cache_ttl = st.slider("Cache TTL (seconds):", 0, 3600, 300, 10)
    else:
        max_steps = None
<<<<<<< HEAD
    
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
=======
        cache_ttl = None

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================
# DISPLAY CHAT HISTORY
# =========================
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
>>>>>>> 796463936eb27059360248792004d25343f046ac
        st.markdown(message["content"])


# =========================
# FALLBACK LOGIC
# =========================
def run_with_fallback(prompt, mode, provider_choice, max_steps=None, cache_ttl=None):

    def run_gemini():
        if mode == "🤖 Agent (Real-time API)":
            llm = GeminiProvider()
            agent = ReActAgent(llm=llm, max_steps=max_steps, cache_ttl=cache_ttl)
            return agent.run(prompt)
        else:
            chatbot = GeminiChatbot()
            return chatbot.chat(prompt)

    def run_openai():
        if mode == "🤖 Agent (Real-time API)":
            llm = OpenAIProvider()
            agent = ReActAgent(llm=llm, max_steps=max_steps, cache_ttl=cache_ttl)
            return agent.run(prompt)
        else:
            chatbot = OpenAIChatbot()
            return chatbot.chat(prompt)

    # =====================
    # MANUAL MODE
    # =====================
    if provider_choice == "Gemini":
        return run_gemini(), "Gemini"

    if provider_choice == "OpenAI":
        return run_openai(), "OpenAI"

    # =====================
    # AUTO FALLBACK MODE
    # =====================
    try:
        result = run_gemini()
        return result, "Gemini"

    except Exception as gemini_error:
        logger.log_event("FALLBACK_TRIGGERED", {
            "provider": "gemini",
            "error": str(gemini_error)
        })

        print("⚠️ Gemini failed → switching to OpenAI")

        try:
            result = run_openai()
            return result, "OpenAI (fallback)"

        except Exception as openai_error:
            return {
                "response": f"""❌ Both providers failed:

**Gemini Error:** {str(gemini_error)}

**OpenAI Error:** {str(openai_error)}
"""
            }, "error"


# =========================
# CHAT INPUT
# =========================
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
<<<<<<< HEAD
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
                    
                    agent = ReActAgent(llm=llm, max_steps=max_steps, cache_ttl=cache_ttl)
                    result = agent.run(prompt)
                    response = result["response"]
                    
                    if result.get("cached"):
                        response += "\n\n> ⚡ *Kết quả được tự động lấy từ bộ nhớ đệm (Lịch sử truy vấn) - Tokens: 0*"
                    
                    latency_ms = result.get("latency_ms", 0)
                    tokens = result.get("tokens_used", 0)
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
            
=======

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                result, provider_used = run_with_fallback(
                    prompt, mode, provider_choice, max_steps, cache_ttl
                )

                response = result.get("response", "⚠️ No response returned")

                # Show fallback warning
                if "fallback" in provider_used:
                    st.warning(f"⚠️ Fallback activated → {provider_used}")

                # Show provider
                st.caption(f"Provider: {provider_used}")

                # Cache info
                if result.get("cached"):
                    response += "\n\n> ⚡ *Kết quả được lấy từ cache (0 tokens)*"

                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

>>>>>>> 796463936eb27059360248792004d25343f046ac
            except Exception as e:
                error_msg = f"❌ System Error: {str(e)}"

                st.error(error_msg)
<<<<<<< HEAD
                current_messages.append({
                    "role": current_role,
=======

                st.session_state.messages.append({
                    "role": "assistant",
>>>>>>> 796463936eb27059360248792004d25343f046ac
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